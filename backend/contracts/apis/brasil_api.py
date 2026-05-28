import requests
import time
import re

def cnpj_valido(cnpj):
    cnpj = re.sub(r"\D", "", str(cnpj))

    if len(cnpj) != 14:
        return False

    # evita CNPJs tipo 00000000000000
    if cnpj == cnpj[0] * 14:
        return False

    def calcular_digito(cnpj, pesos):
        soma = sum(int(cnpj[i]) * pesos[i] for i in range(len(pesos)))
        resto = soma % 11
        return "0" if resto < 2 else str(11 - resto)

    pesos1 = [5,4,3,2,9,8,7,6,5,4,3,2]
    pesos2 = [6] + pesos1

    digito1 = calcular_digito(cnpj[:12], pesos1)
    digito2 = calcular_digito(cnpj[:12] + digito1, pesos2)

    return cnpj[-2:] == digito1 + digito2

import random

def validar_cnpj(cnpj):
    cnpj = re.sub(r"\D", "", str(cnpj))

    if not cnpj_valido(cnpj):
        return False, [], 400

    # ══════════════════════════════════════════════════════════════════
    # TENTATIVA 1: BASE PRINCIPAL - BRASIL API
    # ══════════════════════════════════════════════════════════════════
    for tentativa in range(3):
        try:
            time.sleep(random.uniform(1.0, 2.5))
            
            response = requests.get(f"https://brasilapi.com.br/api/cnpj/v1/{cnpj}", timeout=10)

            if response.status_code == 200:
                data = response.json()
                situacao = data.get("descricao_situacao_cadastral", "")
                ativo = situacao == "ATIVA"
                socios = [s["nome_socio"] for s in data.get("qsa", []) if "nome_socio" in s]
                return ativo, socios, 200

            elif response.status_code == 429:
                print(f"[RATE LIMIT] Brasil API bloqueou temporariamente. Tentativa {tentativa + 1}/3. Esperando um pouco...")
                time.sleep(5) # Espera menor antes de tentar de novo ou ir pro fallback
                continue # Tenta de novo no loop

            elif response.status_code == 404:
                print("CNPJ não encontrado na base pública — prosseguindo")
                return True, [], 404

            elif response.status_code == 400:
                return False, [], 400

        except requests.exceptions.RequestException as e:
            print(f"[ERRO REDE] Falha ao conectar na Brasil API: {e}")
            break # Se der timeout ou cair, pula pro plano B

    # ══════════════════════════════════════════════════════════════════
    # PLANO B: FALLBACK COMPLETO - RECEITA WS (Se a Brasil API der 429 ou cair)
    # ══════════════════════════════════════════════════════════════════
    print(f"⚠️ [PLANO B] Acionando contingência via ReceitaWS para o CNPJ: {cnpj}...")
    try:
        response_alt = requests.get(f"https://receitaws.com.br/v1/cnpj/{cnpj}", timeout=10)
        
        if response_alt.status_code == 200:
            data_alt = response_alt.json()
            
            if data_alt.get("status") == "ERROR":
                print("CNPJ não localizado ou inválido na ReceitaWS.")
                return True, [], 404
                
            situacao = data_alt.get("situacao", "")
            ativo = situacao == "ATIVA"
            
            socios = [s["nome"] for s in data_alt.get("qsa", []) if "nome" in s]
            
            print("✅ [SUCESSO PLANO B] Dados recuperados via ReceitaWS!")
            return ativo, socios, 200
            
    except Exception as e:
        print(f"❌ Plano B também falhou: {e}")

    return False, [], 500