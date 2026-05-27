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

def validar_cnpj(cnpj):

    cnpj = re.sub(r"\D", "", str(cnpj))

    if not cnpj_valido(cnpj):
        return False, [], 400

    for tentativa in range(5):

        response = requests.get(f"https://brasilapi.com.br/api/cnpj/v1/{cnpj}")

        if response.status_code == 200:

            data = response.json()

            situacao = data.get("descricao_situacao_cadastral", "")
            ativo = situacao == "ATIVA"

            socios = [
                s["nome_socio"]
                for s in data.get("qsa", [])
                if "nome_socio" in s
            ]

            return ativo, socios, 200

        elif response.status_code == 429:
            print("Rate limit atingido. Esperando 30s...")
            time.sleep(30)

        elif response.status_code == 404:
            print("CNPJ não encontrado na base pública — prosseguindo")
            return True, [], 404

        elif response.status_code == 400:
            return False, [], 400

        else:
            print("Erro:", response.status_code)
            return False, [], response.status_code

    return False, [], 500