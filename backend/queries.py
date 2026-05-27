import psycopg2
from psycopg2.extras import RealDictCursor

class DashboardQueries:
    def __init__(self, connection_string: str):
        self.conn_string = connection_string

    def _get_connection(self):
        return psycopg2.connect(self.conn_string, cursor_factory=RealDictCursor)

    def obter_tempo_medio_etapas(self) -> list[dict]:
        query = """
            WITH tempos AS (
                SELECT 
                    lead_id,
                    status_novo AS etapa,
                    criado_em AS data_entrada,
                    LEAD(criado_em) OVER (PARTITION BY lead_id ORDER BY criado_em) AS data_saida
                FROM lead_status_history
            )
            SELECT 
                etapa,
                ROUND(AVG(EXTRACT(EPOCH FROM (data_saida - data_entrada))/86400)::numeric, 1) as media_dias
            FROM tempos
            WHERE data_saida IS NOT NULL
            GROUP BY etapa;
        """
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query)
                return cur.fetchall()

    def obter_historico_conversoes_temporais(self) -> list[dict]:
        query = """
            SELECT lead_id, status_anterior, status_novo, criado_em 
            FROM lead_status_history 
            ORDER BY criado_em ASC;
        """
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query)
                return cur.fetchall()