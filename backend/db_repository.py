import psycopg2
from psycopg2.extras import RealDictCursor, execute_values
from datetime import date, datetime
import streamlit as st

class LeadRepository:
    def __init__(self, connection_string: str):
        self.conn_string = connection_string

    def _get_connection(self):
        return psycopg2.connect(self.conn_string, cursor_factory=RealDictCursor)

    def listar_todos(self) -> list[dict]:
        query = "SELECT * FROM leads ORDER BY criado_em DESC;"
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query)
                return cur.fetchall()

    def inserir(self, lead: dict) -> None:
        query = """
            INSERT INTO leads (
                nome_fantasia, responsavel_agendamento, responsavel_venda, 
                data_reuniao, segmento, estado, num_funcionarios, 
                num_lojas, ticket_medio, total_pecas, origem_lista, status, forms_enviado
            ) VALUES (
                %(nome_fantasia)s, %(responsavel_agendamento)s, %(responsavel_venda)s, 
                %(data_reuniao)s, %(segmento)s, %(estado)s, %(num_funcionarios)s, 
                %(num_lojas)s, %(ticket_medio)s, %(total_pecas)s, %(origem_lista)s, %(status)s, %(forms_enviado)s
            );
        """
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, lead)
            conn.commit()

    def atualizar_status(self, lead_id: int, novo_status: str, forms_enviado: bool = None) -> None:
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT status FROM leads WHERE id = %s;", (lead_id,))
                resultado = cur.fetchone()
                status_anterior = resultado["status"] if resultado else None

                if status_anterior == novo_status:
                    return

                if forms_enviado is not None:
                    query_lead = "UPDATE leads SET status = %s, forms_enviado = %s, atualizado_em = NOW() WHERE id = %s;"
                    params_lead = (novo_status, forms_enviado, lead_id)
                else:
                    query_lead = "UPDATE leads SET status = %s, atualizado_em = NOW() WHERE id = %s;"
                    params_lead = (novo_status, lead_id)
                
                cur.execute(query_lead, params_lead)

                query_history = """
                    INSERT INTO lead_status_history (lead_id, status_anterior, status_novo)
                    VALUES (%s, %s, %s);
                """
                cur.execute(query_history, (lead_id, status_anterior, novo_status))
                
            conn.commit()


class BancoDadosManager:
    def __init__(self):
        self.conn_string = st.secrets['postgres']['DATABASE_URL']
            
        if not self.conn_string:
            raise KeyError("❌ URI do banco de dados não encontrada no secrets.toml!")

    def _get_conexao(self):
        # Conecta direto usando a URI, sem precisar quebrar em host, user, etc.
        return psycopg2.connect(self.conn_string)

    def salvar_lead(self, dados_lead: dict) -> bool:
        """Salva um único lead comercial aplicando o filtro de prevenção de duplicatas."""
        query = """
            INSERT INTO leads_prospecção_inteligente 
            (nome_empresa, segmento, regiao_cidade, telefone, site, rating_maps, 
             total_reviews, endereco_completo, place_id_google, tendencia_buzz, 
             sentimento_reviews_medio, score_heuristico)
            VALUES 
            (%(nome_empresa)s, %(segmento)s, %(regiao_cidade)s, %(telefone)s, %(site)s, %(rating_maps)s, 
             %(total_reviews)s, %(endereco_completo)s, %(place_id_google)s, %(tendencia_buzz)s, 
             %(sentimento_reviews_medio)s, %(score_heuristico)s)
            ON CONFLICT (place_id_google) DO NOTHING;
        """
        
        # 2. Usando o gerenciador de contexto 'with' igualzinho à classe LeadRepository!
        # Isso garante que se der erro, o 'conn.rollback()' e o 'close()' acontecem sozinhos.
        try:
            with self._get_conexao() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, dados_lead)
                    # No psycopg2, se houver ON CONFLICT DO NOTHING e o registro já existir,
                    # o rowcount retorna 0. Se for inserido, retorna 1.
                    foi_inserido = cursor.rowcount > 0
                conn.commit()
            return foi_inserido
            
        except Exception as e:
            print(f"❌ Erro ao salvar lead no Postgres: {e}")
            return False