from maps import MAPA_REGIOES, MAPA_SEGMENTOS, PIPELINE, ETAPAS_FINAIS, VENDEDORAS, RESPONSAVEL
from db_dash import _db_listar_leads, _db_salvar_lead, _db_atualizar_status
from datetime import date
import streamlit as st

def _todos_vendedores() -> list[str]:
    nomes: set[str] = set()
    for l in _db_listar_leads():
        if l.get("responsavel_venda"):
            nomes.add(l["responsavel_venda"])
    return sorted(nomes)

def _todos_agendadores() -> list[str]:
    nomes: set[str] = set()
    for l in _db_listar_leads():
        if l.get("responsavel_agendamento"):
            nomes.add(l["responsavel_agendamento"])
    return sorted(nomes)

def _todos_responsaveis() -> list[str]:
    nomes: set[str] = set()
    for l in _db_listar_leads():
        if l.get("responsavel_agendamento"):
            nomes.add(l["responsavel_agendamento"])
        if l.get("responsavel_venda"):
            nomes.add(l["responsavel_venda"])
    return sorted(nomes)


def _proximo_passo_linear(status: str) -> str | None:
    """Retorna próximo status no pipeline linear (ignora ramificações tratadas na UI)."""
    if status in ETAPAS_FINAIS or status in ("Agendado", "No Show"):
        return None
    try:
        idx = PIPELINE.index(status)
        for nxt in PIPELINE[idx + 1:]:
            if nxt not in ("Perda / Caiu",):
                return nxt
    except (ValueError, IndexError):
        pass
    return None


def _mover_lead(lead_id: int, novo_status: str) -> None:
    forms = True if novo_status == "Tô Dentro" else None
    _db_atualizar_status(lead_id, novo_status, forms)
    st.rerun()


def _leads_filtrados(leads: list[dict], filtro_agend: str | None, filtro_venda: str | None) -> list[dict]:
    if filtro_agend:
        leads = [l for l in leads if l.get("responsavel_agendamento") == filtro_agend]
    if filtro_venda:
        leads = [l for l in leads if l.get("responsavel_venda") == filtro_venda]
    return leads


def _fmt_date(d) -> str:
    if isinstance(d, date):
        return d.strftime("%d/%m/%Y")
    return str(d) if d else "—"