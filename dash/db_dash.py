import streamlit as st
import sys
from pathlib import Path

caminho_atual = Path(__file__).resolve()
diretorio_raiz = caminho_atual.parent.parent
if str(diretorio_raiz) not in sys.path:
    sys.path.append(str(diretorio_raiz))

from backend.db_repository import LeadRepository
# 1. IMPORTA SUA NOVA CLASSE DE QUERIES ANALÍTICAS
from backend.queries import DashboardQueries

# Instancia os dois motores com a string de conexão
repo = LeadRepository(st.secrets["postgres"]["DATABASE_URL"])
queries_dash = DashboardQueries(st.secrets["postgres"]["DATABASE_URL"])

# ──────────────────────────────────────────────────────────────────
# 2. CAMADA DE DADOS OPERACIONAIS (CRM / KANBAN)
# ──────────────────────────────────────────────────────────────────

def _db_listar_leads() -> list[dict]:
    """Retorna todos os leads vindos diretamente do banco de dados."""
    return repo.listar_todos()

def _db_salvar_lead(lead: dict) -> None:
    """Insere um novo lead no banco de dados."""
    repo.inserir(lead)

def _db_atualizar_status(lead_id: int, novo_status: str, forms_enviado: bool | None = None) -> None:
    """Atualiza o status (e opcionalmente forms_enviado) de um lead no banco."""
    repo.atualizar_status(lead_id, novo_status, forms_enviado)

# ──────────────────────────────────────────────────────────────────
# 3. CAMADA DE INTELIGÊNCIA (DASHBOARD & BUSINESS INTELLIGENCE)
# ──────────────────────────────────────────────────────────────────

def _db_obter_tempo_medio_etapas() -> list[dict]:
    """Busca a métrica de ciclo de vida (velocidade do funil) do banco."""
    return queries_dash.obter_tempo_medio_etapas()

def _db_obter_historico_conversoes_temporais() -> list[dict]:
    """Puxa o histórico de transições completo para os filtros dinâmicos do Gustavo."""
    return queries_dash.obter_historico_conversoes_temporais()