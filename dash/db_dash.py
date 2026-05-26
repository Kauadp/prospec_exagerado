import streamlit as st
import sys
from pathlib import Path

caminho_atual = Path(__file__).resolve()
diretorio_raiz = caminho_atual.parent.parent
if str(diretorio_raiz) not in sys.path:
    sys.path.append(str(diretorio_raiz))
from backend.db_repository import LeadRepository
repo = LeadRepository(st.secrets["postgres"]["DATABASE_URL"])

# ──────────────────────────────────────────────────────────────────
# 2. CAMADA DE DADOS — INTEGRADA AO POSTGRESQL
# ──────────────────────────────────────────────────────────────────

def _db_listar_leads() -> list[dict]:
    """
    Retorna todos os leads vindos diretamente do banco de dados.
    """
    return repo.listar_todos()


def _db_salvar_lead(lead: dict) -> None:
    """
    Insere um novo lead no banco de dados.
    """
    repo.inserir(lead)


def _db_atualizar_status(lead_id: int, novo_status: str, forms_enviado: bool | None = None) -> None:
    """
    Atualiza o status (e opcionalmente forms_enviado) de um lead no banco.
    O método do repositório já cuida de atualizar a tabela principal e 
    gerar o log na tabela de histórico de transições.
    """
    repo.atualizar_status(lead_id, novo_status, forms_enviado)