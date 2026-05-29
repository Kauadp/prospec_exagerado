import pandas as pd
from num2words import num2words
import requests
from io import BytesIO
import re

def carregar_expositores(url):
    """
    Carrega a planilha de expositores e faz limpeza básica.
    
    Args:
        url: URL da planilha Excel a carregar (obrigatório)
    
    Returns:
        DataFrame com expositores filtrados
        
    Raises:
        ValueError: Se URL não for fornecida
        RequestException: Se houver erro ao baixar a planilha
    """
    if not url:
        raise ValueError(
            "URL da planilha não foi fornecida. "
            "Use EventoService.obter_url_planilha() para obter a URL do evento."
        )

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(url, headers=headers)
    response.raise_for_status()

    file = BytesIO(response.content)
    df = pd.read_excel(file, sheet_name="Sheet1")
    
    df.columns = df.columns.str.strip()

    df = df.fillna("")

    print(f"[DEBUG] Colunas encontradas na planilha: {list(df.columns)}")

    return df


def limpar_texto(valor):
    """
    Remove espaços extras de textos.
    """

    if isinstance(valor, str):
        return valor.strip()

    return valor

def valor_entrada(valor):
    """
    Calcula 10% de entrada.
    """

    return .1 * valor


def valor_restante(valor):
    """
    Calcula 90% restantes.
    """

    return .9 * valor


def limpar_valor(valor):
    """
    Converte valores no formato brasileiro para float.
    Aceita:
    - R$ 1.234,56
    - 1.234,56
    - 1234,56
    - 1234.56
    - "", NaN
    """

    if valor == "" or pd.isna(valor):
        return 0.0

    if isinstance(valor, (int, float)):
        return float(valor)

    if isinstance(valor, str):
        valor = re.sub(r"[^\d,.\-]", "", valor)

        if "," in valor:
            valor = valor.replace(".", "")
            valor = valor.replace(",", ".")

    return float(valor)


def formatar_real(valor):
    """
    Formata valores para R$.
    """
     
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def extrair_percentual_comissionado(valor_comissionado):
    """
    Extrai percentual no formato "X%" e retorna decimal.
    Exemplos:
    - "5%" -> 0.05
    - "12,5%" -> 0.125
    - "", NA, NULO -> None
    """
    if valor_comissionado is None or pd.isna(valor_comissionado):
        return None

    texto = str(valor_comissionado).strip().upper()
    if texto in {"", "NA", "N/A", "NULO", "NULL", "-"}:
        return None

    if "%" not in texto:
        numero_limpo = texto.replace(",", ".")
        try:
            numero = float(numero_limpo)
            if numero <= 1:
                return numero
            return numero / 100
        except ValueError:
            return None

    match = re.search(r"(\d+(?:[.,]\d+)?)\s*%", texto)
    if not match:
        return None

    percentual = match.group(1).replace(",", ".")
    return float(percentual) / 100


def calcular_valor_total_comissionado(valor_minimo_garantido, percentual_comissionado):
    """
    Calcula o valor total de faturamento necessário para cobrir a comissão.
    Fórmula: mínimo_garantido / percentual
    """
    if not percentual_comissionado:
        return None

    return valor_minimo_garantido / percentual_comissionado


def limpar_telefone(telefone_bruto) -> str:
    """
    Trata o input do cliente e garante o formato internacional padrão: 55DDD9XXXXXXXX
    Retorna string vazia se o número for inválido ou impossível de deduzir o DDD.
    """
    if not telefone_bruto or str(telefone_bruto).lower() == "nan":
        return ""        
    nums = re.sub(r"\D", "", str(telefone_bruto))    
    if nums.startswith("0"):
        nums = nums[1:]
        
    length = len(nums)    
    if length in (12, 13) and nums.startswith("55"):
        return nums        
    if length in (10, 11):
        return f"55{nums}"
        
    if length == 9 or length == 8:
        ddd_padrao = "27" 
        print(f"[AVISO TELEFONE] Cliente esqueceu o DDD. Aplicando fallback {ddd_padrao} para o número {nums}")
        return f"55{ddd_padrao}{nums}"
        
    print(f"[ERRO TELEFONE] Número impossível de tratar: {telefone_bruto}")
    return ""

def preparar_expositor(row):
    nome_fantasia = limpar_texto(row.get("Nome Fantasia", "SEM NOME"))
    
    print(f"[DEBUG] Processando dados cadastrais da planilha para: {nome_fantasia}")

    expositor = {
        #### DADOS CADASTRAIS BRUTOS (Vêm do Forms) ####
        "EXPOSITOR": limpar_texto(row["Razão social"]),
        "NOMEFANTASIAEXPOSITOR": nome_fantasia,
        "CNPJEXPOSITOR": limpar_texto(row["CNPJ"]),
        "INSCRICAOESTADUALEXPOSITOR": limpar_texto(row["Inscrição Estadual"]),
        "ENDERECOSEDEEXPOSITOR": limpar_texto(row["Endereço comercial"]),
        "FUNCAOCONTRATUALEXPOSITOR": "Proprietário",
        "RESPONSAVELCONTRATUALEXPOSITOR": limpar_texto(row["Nome completo (Sócio proprietário)"]),
        "CPFRESPONSAVELCONTRATUALEXPOSITOR": limpar_texto(row["CPF (TITULAR CNPJ)"]),
        "RGRESPONSALVELCONTRATUALEXPOSITOR": limpar_texto(row["RG (TITULAR CNPJ)"]),
        "LISTADEMARCAS": limpar_texto(row["Marcas (que você levará para o evento)"]),

        #### FOOD COMPATIBILIDADE ####
        "DOCUMENTOREPRESENTENTAEXPOSITOR": nome_fantasia,
        "DOCUMENTOEXPOSITOR": limpar_texto(row["CPF (TITULAR CNPJ)"]),
        "RAZAOEXPOSITOR2": limpar_texto(row["Razão social"]),
        "DOCUMENTOEXPOSITOR2": limpar_texto(row["CPF (TITULAR CNPJ)"])
    }

    return expositor