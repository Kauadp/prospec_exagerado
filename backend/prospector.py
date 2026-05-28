import time
import random
from LeIA import SentimentIntensityAnalyzer
from backend.conector_google import ConectorGoogleMaps
from backend.db_repository import BancoDadosManager
from dash.maps import MAPA_SEGMENTOS 

class LeadProspector:
    def __init__(self):
        # Instancia os sub-módulos focados no ecossistema estável
        self.conector_google = ConectorGoogleMaps()
        self.db = BancoDadosManager()
        # Inicializa o analisador de sentimento em português
        self.analyzer = SentimentIntensityAnalyzer()

    def calcular_score(self, rating: float, total_reviews: int) -> float:
        """Aplica heurística para pontuar o lead (Maior score = Maior maturidade)."""
        fator_volume = total_reviews / 100.0
        score_final = (rating * 4) + fator_volume
        return round(min(score_final, 30.0), 2) # Limitador teto de segurança

    def executar_fluxo_prospeccao(self, segmento: str, cidade_regiao: str) -> int:
        # --- HIGIENIZAÇÃO DE STRING PARA A API DO GOOGLE ---
        segmento_limpo = segmento.replace("&", "e").strip()
        cidade_limpa = cidade_regiao.split("(")[0].strip() 
        # ---------------------------------------------------

        print(f"\n🚀 [LeadProspector] Iniciando esteira focada em Google Maps para '{segmento_limpo}' em '{cidade_limpa}'...")

        # 1. Ativa a inteligência de expansão por sinônimos do seu dicionário
        config_segmento = MAPA_SEGMENTOS.get(segmento, {"termos_bio": [segmento_limpo]})
        termos_busca_expandidos = config_segmento.get("termos_bio", [segmento_limpo])

        print(f"🔥 [LeadProspector] Matriz de busca expandida: {termos_busca_expandidos}")

        empresas_totais = []

        # 2. Executa a varredura real/mock no Google Maps para cada termo do dicionário
        for termo in termos_busca_expandidos:
            termo_query = termo.replace("&", "e").strip()
            print(f"🔍 [Google Maps] Executando Text Search para: '{termo_query} em {cidade_limpa}'")
            
            # Aqui ele puxa o JSON com nome, rating, site, telefone e as reviews!
            empresas_encontradas = self.conector_google.buscar_empresas_por_tendencia(termo_query, cidade_limpa)
            empresas_totais.extend(empresas_encontradas)

        # Remove duplicados caso o mesmo estabelecimento apareça em mais de um sinônimo
        empresas_unicas = {e['place_id_google']: e for e in empresas_totais if e.get('place_id_google')}.values()
        
        novos_leads_contador = 0

        # 3. Processa, qualifica e analisa o sentimento das reviews de cada lead
        for empresa in empresas_unicas:
            print(f"\n📊 Processando inteligência do lead: {empresa['nome_fantasia']}")
            
            # Extrai e calcula o sentimento das reviews reais que vieram do Google
            scores_reviews = []
            for review in empresa["reviews_extraidas"]:
                score_sentimento = self.analyzer.polarity_scores(review)
                scores_reviews.append(score_sentimento["compound"])
            
            # Tira a média do sentimento (-1 a 1)
            sentimento_medio = sum(scores_reviews) / len(scores_reviews) if scores_reviews else 0.0

            # Calcula a heurística de priorização comercial
            score_comercial = self.calcular_score(empresa["rating_maps"], empresa["total_reviews"])

            # Estrutura o payload idêntico ao esperado pelas colunas do Postgres
            payload_lead = {
                "nome_empresa": empresa["nome_fantasia"],
                "segmento": segmento,
                "regiao_cidade": cidade_regiao,
                "telefone": empresa["telefone"],
                "site": empresa["site"],
                "rating_maps": empresa["rating_maps"],
                "total_reviews": empresa["total_reviews"],
                "endereco_completo": empresa["endereco_completo"],
                "place_id_google": empresa["place_id_google"],
                "tendencia_buzz": f"Busca Expandida: {segmento_limpo}", # Marcador limpo
                "sentimento_reviews_medio": round(sentimento_medio, 2),
                "score_heuristico": score_comercial
            }

            # 4. Envia para o repositório persistir e tratar duplicidade no Postgres
            inserido = self.db.salvar_lead(payload_lead)
            if inserido:
                print(f"✅ [LeadProspector] Novo lead armazenado! Score: {score_comercial}")
                novos_leads_contador += 1
            else:
                print(f"Skip: Lead '{empresa['nome_fantasia']}' já existe no banco.")

        print(f"\n🏁 [LeadProspector] Varredura finalizada. {novos_leads_contador} novos registros reais inseridos.")
        return novos_leads_contador