"""
Configuração centralizada para múltiplos eventos.
Define metadados por evento: URLs de planilhas, tokens, tipos de stands, templates, etc.
"""

from typing import List, Dict


class EventoConfig:
    """
    Configuração de um evento.
    """
    def __init__(
        self,
        sigla: str,
        nome: str,
        excel_url_env: str = None,
        autentique_token_env: str = None,
        tipos_stand: List[str] = None,
        formas_pagamento: List[str] = None,
        templates_disponiveis: bool = True,
        descricao: str = ""
    ):
        self.sigla = sigla  # ex: "ES", "RJ"
        self.nome = nome    # ex: "Espírito Santo"
        
        # Credenciais: variáveis de ambiente para este evento
        self.excel_url_env = excel_url_env or f"EXCEL_URL_{sigla}"
        self.autentique_token_env = autentique_token_env or f"AUTENTIQUE_API_TOKEN_{sigla}"
        
        self.tipos_stand = tipos_stand or ["STAND", "FOOD"]
        self.formas_pagamento = formas_pagamento or [
            "10% DE ENTRADA E O RESTANTE PARCELADO EM ATÉ 6X SEM JUROS",
            "PIX COM 5% DE DESCONTO"
        ]
        self.templates_disponiveis = templates_disponiveis
        self.descricao = descricao


# Mapa de eventos registrados
EVENTOS = {
    "RJ": EventoConfig(
        sigla="RJ",
        nome="Rio de Janeiro",
        excel_url_env="EXCEL_URL_RJ",
        autentique_token_env="AUTENTIQUE_API_TOKEN_RJ",
        tipos_stand=["STAND", "FOOD"],
        formas_pagamento=[
            "10% DE ENTRADA E O RESTANTE PARCELADO EM ATÉ 6X SEM JUROS",
            "PIX COM 5% DE DESCONTO"
        ],
        templates_disponiveis=True,
        descricao="Evento RJ"
    ),
}


EVENTO_PADRAO = "RJ"


def obter_evento(sigla: str = None) -> EventoConfig:
    """
    Obtém a configuração de um evento.
    Se sigla é None, usa o evento padrão (ES).
    """
    if sigla is None:
        sigla = EVENTO_PADRAO

    if sigla not in EVENTOS:
        raise ValueError(
            f"Evento '{sigla}' não encontrado. "
            f"Eventos disponíveis: {', '.join(EVENTOS.keys())}"
        )

    return EVENTOS[sigla]


def listar_eventos() -> Dict[str, EventoConfig]:
    """
    Retorna dicionário de todos os eventos registrados.
    """
    return EVENTOS.copy()


def verificar_evento_existe(sigla: str) -> bool:
    """
    Verifica se um evento está registrado.
    """
    return sigla in EVENTOS

