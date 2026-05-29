import os
import sys
import time
import subprocess
import psycopg2
from psycopg2.extras import RealDictCursor
import streamlit as st
from docxtpl import DocxTemplate
import re
from backend.contracts.config.eventos import obter_evento
from backend.contracts.apis.autentique import enviar_para_autentique
from backend.contracts.apis.brasil_api import validar_cnpj  
from backend.contracts.get_data import (
    formatar_real, valor_entrada, valor_restante, 
    carregar_expositores, preparar_expositor, limpar_telefone
)

def obter_conexao():
    return psycopg2.connect(st.secrets["postgres"]["DATABASE_URL"], cursor_factory=RealDictCursor)

class ContractService:
    def __init__(self, sigla_evento: str = "RJ"):
        self.sigla_evento = sigla_evento.upper()
        self.config = obter_evento(self.sigla_evento)
        self.excel_url = "EXCEL_URL_" + self.sigla_evento

    def sincronizar_excel_para_postgres(self, callback_log=None) -> dict:
        """
        FASE 1: Varre a planilha, aplica o cache inteligente por CNPJ,
        valida os novos e insere no banco com status 'Aguardando Vínculo'.
        """
        try:
            url_planilha = st.secrets["EXCEL_URLS"][self.excel_url]
        except KeyError:
            return {"status": "erro", "mensagem": f"URL do Excel para {self.sigla_evento} não configurada no st.secrets."}

        if callback_log:
            callback_log("📥 Conectando ao OneDrive/SharePoint do Rio de Janeiro...")

        try:
            df = carregar_expositores(url=url_planilha)
            if callback_log:
                callback_log(f"📋 Planilha importada com sucesso! Encontradas {len(df)} empresas com status 'Aguardando'.")
        except Exception as e:
            return {"status": "erro", "mensagem": f"Erro ao acessar ou ler a planilha Excel 365: {e}"}

        inseridos = 0
        pula_cache = 0
        erros_validacao = []

        for _, row in df.iterrows():
            try:
                cnpj_limpo = re.sub(r"\D", "", str(row.get("CNPJ", "")))
                if not cnpj_limpo:
                    continue
                
                nome_fantasia = row.get("Nome Fantasia", "Sem Nome Fantasia")

                if callback_log:
                    callback_log(f"🔎 Analisando histórico e cache local de: <b>{nome_fantasia}</b>...")

                with obter_conexao() as conn:
                    with conn.cursor() as cur:
                        cur.execute("SELECT id, status_automacao FROM contratos_pendentes WHERE cnpj = %s LIMIT 1", (cnpj_limpo,))
                        existe_no_banco = cur.fetchone()

                if existe_no_banco:
                    pula_cache += 1
                    if callback_log:
                        callback_log(f"⏭️ Cache ativo para {nome_fantasia} (Status: {existe_no_banco['status_automacao']}). Pulando chamada de API.")
                    continue

                if callback_log:
                    callback_log(f"🌐 <b>{nome_fantasia}</b> é inédito. Consultando base federal da Receita...")
                
                exp = preparar_expositor(row)
                email_valido = row.get("E-mail (Sócio proprietário)", "")
                tel_socio = limpar_telefone(row.get("Telefone (Sócio proprietário)", ""))

                ativo, socios, status_cnpj = validar_cnpj(cnpj_limpo)

                if status_cnpj != 200 or not ativo:
                    erros_validacao.append(f"❌ {exp['NOMEFANTASIAEXPOSITOR']} - CNPJ {cnpj_limpo} Inválido/Inativo.")
                    continue

                if not email_valido:
                    erros_validacao.append(f"❌ {exp['NOMEFANTASIAEXPOSITOR']} - E-mail ausente.")
                    continue

                nome_socio = exp["RESPONSAVELCONTRATUALEXPOSITOR"] if exp["RESPONSAVELCONTRATUALEXPOSITOR"] else (socios[0] if socios else "Não Informado")

                with obter_conexao() as conn:
                    with conn.cursor() as cur:
                        cur.execute("""
                            INSERT INTO contratos_pendentes (
                                sigla_evento, razao_social, nome_fantasia, cnpj,
                                inscricao_estadual, endereco_comercial, nome_socio,
                                cpf_socio, rg_socio, marcas_expositor, email_socio,
                                telefone_socio,
                                valor_total, valor_entrada, valor_restante,
                                forma_pagamento, status_automacao
                            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 0.00, 0.00, 0.00, %s, 'Aguardando Vínculo')
                            ON CONFLICT (cnpj) DO NOTHING;
                        """, (
                            self.sigla_evento, exp["EXPOSITOR"], exp["NOMEFANTASIAEXPOSITOR"], cnpj_limpo,
                            exp["INSCRICAOESTADUALEXPOSITOR"], exp["ENDERECOSEDEEXPOSITOR"], nome_socio,
                            exp["CPFRESPONSAVELCONTRATUALEXPOSITOR"], exp["RGRESPONSALVELCONTRATUALEXPOSITOR"],
                            exp["LISTADEMARCAS"], email_valido, 
                            tel_socio, row.get("Forma de pagamento", "")
                        ))
                    conn.commit()
                
                inseridos += 1
                if callback_log:
                    callback_log(f"💾 <b>{nome_fantasia}</b> cadastrado na base migratória com status 'Aguardando Vínculo'!")

            except Exception as line_error:
                print(f"Erro na linha: {line_error}")
                continue

        return {
            "status": "sucesso",
            "mensagem": f"Sincronização concluída! {inseridos} novos inseridos, {pula_cache} ignorados pelo cache.",
            "alertas": erros_validacao
        }

    # ══════════════════════════════════════════════════════════════════
    # APENAS GERAR A MINUTA EM WORD (.DOCX)
    # ══════════════════════════════════════════════════════════════════
    def gerar_apenas_docx(self, id_solicitacao: int) -> tuple:
        """Busca os dados no Postgres, renderiza o template e salva o arquivo .docx físico."""
        try:
            with obter_conexao() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT * FROM contratos_pendentes WHERE id = %s", (id_solicitacao,))
                    contrato = cur.fetchone()

            if not contrato:
                return False, "Contrato não localizado no banco."

            modulo_dados = __import__(f"backend.contracts.dados_evento.{self.sigla_evento.lower()}", fromlist=[""])
            dados_tipo = modulo_dados.evento_stand if contrato["tipo_stand"] == "STAND" else modulo_dados.evento_food

            valor_numeric = float(contrato["valor_total"])
            entrada_numeric = valor_entrada(valor_numeric)
            restante_numeric = valor_restante(valor_numeric)

            expositor_context = {
                "EXPOSITOR": contrato["razao_social"],
                "NOMEFANTASIAEXPOSITOR": contrato["nome_fantasia"],
                "CNPJEXPOSITOR": contrato["cnpj"],
                "INSCRICAOESTADUALEXPOSITOR": contrato["inscricao_estadual"],
                "ENDERECOSEDEEXPOSITOR": contrato["endereco_comercial"],
                "FUNCAOCONTRATUALEXPOSITOR": "Proprietario",
                "RESPONSAVELCONTRATUALEXPOSITOR": contrato["nome_socio"],
                "CPFRESPONSAVELCONTRATUALEXPOSITOR": contrato["cpf_socio"],
                "RGRESPONSALVELCONTRATUALEXPOSITOR": contrato["rg_socio"],
                "LISTADEMARCAS": contrato["marcas_expositor"],
                "STANDNUMERO": contrato["stand_endereco"],
                "EXPOSITORAREASTAND": contrato["metragem"],
                "VALORTOTALALUGUELSTAND": formatar_real(valor_numeric),
                "ENTRADAVALOR": formatar_real(entrada_numeric),
                "VALORRESTANTE": formatar_real(restante_numeric),
                "DOCUMENTOREPRESENTENTAEXPOSITOR": contrato["nome_fantasia"],
                "DOCUMENTOEXPOSITOR": contrato["cpf_socio"],
                "RAZAOEXPOSITOR2": contrato["razao_social"],
                "DOCUMENTOEXPOSITOR2": contrato["cpf_socio"]
            }

            context = {**dados_tipo, **expositor_context}

            # Mapeia template
            pagamento_prefix = "parcelado" if "PARCELADO" in contrato["forma_pagamento"].upper() else "avista"
            tipo_prefix = "food_" if contrato["tipo_stand"] == "FOOD" else ""
            nome_template = f"template_{tipo_prefix}{pagamento_prefix}_{self.sigla_evento.lower()}.docx"
            
            caminho_template = os.path.join("template", nome_template)
            if not os.path.exists(caminho_template):
                return False, f"Template {nome_template} não localizado."

            # Renderiza
            doc = DocxTemplate(caminho_template)
            doc.render(context)

            os.makedirs("contratos", exist_ok=True)
            nome_base = f"contrato_{contrato['nome_fantasia'].replace(' ', '_').lower()}"
            caminho_docx = os.path.join("contratos", f"{nome_base}.docx")
            
            doc.save(caminho_docx)
            caminho_libreoffice_windows = r"C:\Program Files\LibreOffice\program\soffice.exe"
            
            tem_windows_libre = os.path.exists(caminho_libreoffice_windows)
            tem_linux_libre = subprocess.run(["which", "libreoffice"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0 if os.name != 'nt' else False

            if tem_windows_libre or tem_linux_libre:
                comando_cmd = [caminho_libreoffice_windows, "--headless", "--convert-to", "pdf", "--outdir", "contratos", caminho_docx] if tem_windows_libre else ["libreoffice", "--headless", "--convert-to", "pdf", "--outdir", "contratos", caminho_docx]
                subprocess.run(comando_cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            else:
                print("[AVISO DEVELOPMENT] LibreOffice não localizado. Pulando geração do PDF de preview.")
            return True, caminho_docx

        except Exception as e:
            print(f"[ERRO WORD] {e}")
            return False, str(e)

    # ══════════════════════════════════════════════════════════════════
    # CONVERTER EM PDF E MANDAR PARA A AUTENTIQUE
    # ══════════════════════════════════════════════════════════════════
    def converter_pdf_e_disparar_autentique(self, id_solicitacao: int, caminho_docx: str, modo_teste: bool = False) -> dict:
        """Pega o arquivo DOCX gerado, passa pelo LibreOffice Headless, envia à API e atualiza os status."""
        try:
            with obter_conexao() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT * FROM contratos_pendentes WHERE id = %s", (id_solicitacao,))
                    contrato = cur.fetchone()

            if not contrato:
                return {"status": "erro", "mensagem": "Contrato não encontrado no banco."}

            nome_base = f"contrato_{contrato['nome_fantasia'].replace(' ', '_').lower()}"
            caminho_pdf = os.path.join("contratos", f"{nome_base}.pdf")

            caminho_libreoffice_windows = r"C:\Program Files\LibreOffice\program\soffice.exe"
            if os.path.exists(caminho_libreoffice_windows):
                comando_cmd = [caminho_libreoffice_windows, "--headless", "--convert-to", "pdf", "--outdir", "contratos", caminho_docx]
            else:
                comando_cmd = ["libreoffice", "--headless", "--convert-to", "pdf", "--outdir", "contratos", caminho_docx]
            
            subprocess.run(comando_cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            if modo_teste:
                return {
                    "status": "sucesso", 
                    "mensagem": "Modo Teste: PDF criado, envio pulado.",
                    "link_assinatura": "https://autentique.com.br/v3/teste-preview",
                    "telefone_socio": contrato.get("telefone_socio")
                }

            try:
                token_autentique = st.secrets["AUTENTIQUE"][f"TOKEN_{self.sigla_evento}"]
            except KeyError:
                return {"status": "erro", "mensagem": f"Token da Autentique não localizado para {self.sigla_evento}."}

            resposta_api = enviar_para_autentique(
                caminho_pdf=caminho_pdf,
                nome_documento=nome_base.upper(),
                nome_signatario=contrato["nome_socio"],
                email_signatario=contrato["email_socio"],
                token_autentique=token_autentique
            )

            if "errors" in resposta_api:
                return {"status": "erro", "mensagem": f"Erro na API da Autentique: {resposta_api['errors']}"}
            
            try:
                dados_assinantes = resposta_api["data"]["createDocument"]["signers"]
                link_assinatura = dados_assinantes[0]["url"] if dados_assinantes else None
            except (KeyError, IndexError, TypeError) as e:
                print(f"Não foi possível extrair a URL da Autentique: {e}")
                link_assinatura = "https://www.autentique.com.br" # Fallback se a API falhar

            with obter_conexao() as conn:
                with conn.cursor() as cur:
                    cur.execute("UPDATE contratos_pendentes SET status_automacao = 'Concluido', updated_at = NOW() WHERE id = %s", (id_solicitacao,))
                    
                    if contrato["lead_id"]:
                        cur.execute("UPDATE leads SET status = 'Contrato Enviado', updated_at = NOW() WHERE id = %s", (contrato["lead_id"],))
                        cur.execute("""
                            INSERT INTO historico_transicoes (lead_id, status_anterior, status_novo, criado_em) 
                            VALUES (%s, 'Tô Dentro', 'Contrato Enviado', NOW())
                        """, (contrato["lead_id"],))
            
                conn.commit()

            return {
                "status": "sucesso", 
                "pdf": caminho_pdf, 
                "link_assinatura": link_assinatura,
                "telefone_socio": contrato.get("telefone_socio")
            }

        except Exception as e:
            return {"status": "erro", "mensagem": f"Erro crítico na pipeline de disparo: {str(e)}"}