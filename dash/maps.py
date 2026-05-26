# ──────────────────────────────────────────────────────────────────
# 1. CONSTANTES DE NEGÓCIO
# ──────────────────────────────────────────────────────────────────

MAPA_REGIOES: dict[str, dict] = {
    "Rio de Janeiro (RJ)": {
        "sufixo_hashtag": "#RJ",
        "termos_bio": ["Rio de Janeiro", "RJ", "carioca", "Niterói", "Zona Sul", "Barra da Tijuca"],
    },
    "São Paulo (SP)": {
        "sufixo_hashtag": "#SP",
        "termos_bio": ["São Paulo", "SP", "paulista", "Brás", "Bom Retiro", "Grande SP"],
    },
}

MAPA_SEGMENTOS: dict[str, dict] = {
    "Moda & Vestuário":   {"prefixo": "moda",      "termos_bio": ["moda", "roupas", "vestuário", "boutique"]},
    "Sapatos":            {"prefixo": "calcados",   "termos_bio": ["sapatos", "calçados", "tênis", "sapataria"]},
    "Joias & Semijoias":  {"prefixo": "joias",      "termos_bio": ["joias", "semijoias", "bijuterias", "folheado"]},
    "Acessórios":         {"prefixo": "acessorios", "termos_bio": ["acessórios", "bolsas", "cintos", "óculos"]},
    "Moda Fitness":       {"prefixo": "fitness",    "termos_bio": ["fitness", "academia", "legging", "sportswear"]},
    "Produtos de Beleza": {"prefixo": "beleza",     "termos_bio": ["beleza", "cosméticos", "skincare", "estética"]},
    "Eletrodomésticos":   {"prefixo": "eletro",     "termos_bio": ["eletrodomésticos", "eletrônicos", "linha branca"]},
    "Atacado":            {"prefixo": "atacado",    "termos_bio": ["atacado", "distribuidor", "atacarejo"]},
}

# Pipeline ordenado — NÃO altere a ordem sem revisar _proximo_passo()
PIPELINE: list[str] = [
    "Agendado",
    "No Show",
    "Perda / Caiu",
    "Reunião Realizada",
    "Tô Dentro",
    "Contrato Enviado",
    "Contrato Assinado",
]

ETAPAS_FINAIS = {"Contrato Assinado", "Perda / Caiu"}

VENDEDORAS: list[str] = [
    "Eliane"
]

RESPONSAVEL: list[str] = [
    "Malu",
    "Henrique"
]

MAPA_METAS: dict[str] = {
    'Malu': {"semanal": 20, "diaria": 4},
    'Henrique': {"semanal": 10, "diaria": 2},
}
