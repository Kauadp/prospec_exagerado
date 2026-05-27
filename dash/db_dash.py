import psycopg2
import streamlit as st
import sys
from pathlib import Path
from psycopg2.extras import RealDictCursor

caminho_atual = Path(__file__).resolve()
diretorio_raiz = caminho_atual.parent.parent
if str(diretorio_raiz) not in sys.path:
    sys.path.append(str(diretorio_raiz))

from backend.db_repository import LeadRepository
# 1. IMPORTA SUA NOVA CLASSE DE QUERIES ANALÍTICAS
from backend.queries import DashboardQueries
from backend.contracts.contract_services import ContractService
from backend.contracts.config.eventos import EVENTOS, EVENTO_PADRAO

# Instancia os dois motores com a string de conexão
repo = LeadRepository(st.secrets["postgres"]["DATABASE_URL"])
queries_dash = DashboardQueries(st.secrets["postgres"]["DATABASE_URL"])

def obter_eventos_disponiveis():
    return EVENTOS, EVENTO_PADRAO

def obter_servico_contratos(sigla_evento: str, callback_log=None) -> dict:
    """Instancia o serviço de contratos e roda a ingestão repassando o logger da tela."""
    service = ContractService(sigla_evento=sigla_evento)
    
    return service.sincronizar_excel_para_postgres(callback_log=callback_log)

# ──────────────────────────────────────────────────────────────────
# 1. CAMADA DE CONTRATOS E SERVIÇOS (INGESTÃO & REGRAS DE NEGÓCIO)
# ──────────────────────────────────────────────────────────────────

def obter_conexao():
    return psycopg2.connect(st.secrets["postgres"]["DATABASE_URL"], cursor_factory=RealDictCursor)

def db_listar_contratos_pendentes(sigla_evento: str) -> list:
    """Busca os contratos na tabela migratória que ainda aguardam vínculo com o CRM."""
    with obter_conexao() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT 
                    id AS id_solicitacao, 
                    razao_social AS nome_formulario, 
                    cnpj, 
                    email_socio AS email
                FROM contratos_pendentes
                WHERE sigla_evento = %s AND status_automacao = 'Aguardando Vínculo'
                ORDER BY criado_em DESC
            """, (sigla_evento.upper(),))
            return cur.fetchall()

def db_listar_leads_no_todentro() -> list:
    """Busca no CRM principal todos os leads estagnados na etapa 'Tô Dentro'."""
    with obter_conexao() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT id, nome_fantasia 
                FROM leads 
                WHERE status = 'Tô Dentro'
                ORDER BY nome_fantasia ASC
            """)
            return cur.fetchall()

def db_vincular_e_enriquecer(id_solicitacao: int, lead_id: int, stand: str, metragem: float, receita: float) -> bool:
    """Salva o enriquecimento e altera o status para liberar a geração do contrato."""
    try:
        v_entrada = .1 * receita
        v_restante = .9 * receita

        with obter_conexao() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    UPDATE contratos_pendentes
                    SET lead_id = %s,
                        stand_endereco = %s,
                        metragem = %s,
                        valor_total = %s,   
                        valor_entrada = %s,    
                        valor_restante = %s,  
                        status_automacao = 'Pronto para Gerar',
                        atualizado_em = NOW()
                    WHERE id = %s
                """, (lead_id, stand, metragem, receita, v_entrada, v_restante, id_solicitacao))
            conn.commit()
        return True
    except Exception as e:
        print(f"[ERRO BANCO] Falha ao enriquecer: {e}")
        return False
    

def db_listar_contratos_prontos_para_gerar(sigla_evento: str) -> list:
    """Busca os contratos que já foram vinculados e enriquecidos, aguardando geração."""
    with obter_conexao() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT 
                    id AS id_solicitacao, 
                    razao_social AS nome_formulario, 
                    nome_fantasia,
                    cnpj, 
                    stand_endereco, 
                    metragem, 
                    valor_total
                FROM contratos_pendentes
                WHERE sigla_evento = %s AND status_automacao = 'Pronto para Gerar'
                ORDER BY atualizado_em ASC
            """, (sigla_evento.upper(),))
            return cur.fetchall()

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