import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import date, datetime

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