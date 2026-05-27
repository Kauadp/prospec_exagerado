import time
import psycopg2
from psycopg2.extras import RealDictCursor
import streamlit as st
from contract_services import ContractService

def obter_conexao():
    return psycopg2.connect(st.secrets["postgres"]["DATABASE_URL"], cursor_factory=RealDictCursor)

def executar_teste_completo():
    print("🎬 INICIANDO TESTE DA PIPELINE DE CONTRATOS (RIO DE JANEIRO)\n")
    
    # Instancia o serviço maestro
    service = ContractService(sigla_evento="RJ")
    
    # ══════════════════════════════════════════════════════════════════
    # FASE 1: INGESTÃO DO EXCEL PARA O POSTGRES
    # ══════════════════════════════════════════════════════════════════
    print("⏳ [FASE 1] Varrendo planilha do Excel 365, tratando e jogando no banco...")
    resultado_sync = service.sincronizar_excel_para_postgres()
    print(f"📊 Retorno da Ingestão: {resultado_sync}\n")
    
    if resultado_sync["status"] == "erro":
        print("❌ Pipeline abortada devido a erro na ingestão.")
        return

    # ══════════════════════════════════════════════════════════════════
    # FASE 2: SIMULAÇÃO DO ENRIQUECIMENTO MANUAL (O QUE A AUXILIAR FARÁ NO DASH)
    # ══════════════════════════════════════════════════════════════════
    print("⏳ [FASE 2] Simulando tratamento de dados e vínculo com o CRM...")
    
    id_para_teste = None
    # Busca a primeira linha que acabou de entrar como 'Aguardando Vínculo'
    with obter_conexao() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT id, nome_fantasia FROM contratos_pendentes 
                WHERE sigla_evento = 'RJ' AND status_automacao = 'Aguardando Vínculo' 
                LIMIT 1
            """)
            registro = cur.fetchone()
            if registro:
                id_para_teste = registro["id"]
                print(f"🏪 Empresa localizada para teste: {registro['nome_fantasia']} (ID Banco: {id_para_teste})")

    if not id_para_teste:
        print("⚠️ Nenhuma empresa nova com status 'Aguardando' foi importada da planilha.")
        print("Verifique se existem linhas com 'Contrato Status' = 'Aguardando' na sua planilha do RJ.")
        return

    # Simula a auxiliar preenchendo o Stand, Metragem, Valor e vinculando ao Lead ID 1 do CRM
    print(f"✍️ Gravando enriquecimento manual para o ID {id_para_teste}...")
    with obter_conexao() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE contratos_pendentes 
                SET lead_id = 1, -- Simulando vínculo com o lead ID 1 do CRM
                    stand_endereco = 'Setor COPACABANA - 05',
                    metragem = 15.0,
                    receita_realizada = 7500.00,
                    tipo_stand = 'STAND',
                    status_automacao = 'Pronto para Gerar',
                    atualizado_em = NOW()
                WHERE id = %s
            """, (id_para_teste,))
        conn.commit()
    print("✅ Dados enriquecidos e integrados. Status alterado para 'Pronto para Gerar'!\n")

    # ══════════════════════════════════════════════════════════════════
    # FASE 3: GERAÇÃO DO DOCUMENTO (MOTOES SÍNCRONOS)
    # ══════════════════════════════════════════════════════════════════
    print(f"⏳ [FASE 3] Disparando geração de documento para o ID {id_para_teste} (Modo Teste)...")
    resultado_geracao = service.emitir_e_disparar_contrato(id_solicitacao=id_para_teste, modo_teste=True)
    
    print("\n🏁 FIM DA PIPELINE")
    print(f"📌 Resultado Final: {resultado_geracao}")

if __name__ == "__main__":
    executar_teste_completo()