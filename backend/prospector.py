import time
import random
from LeIA import SentimentIntensityAnalyzer
from backend.conector_google import ConectorGoogleMaps
from backend.db_repository import BancoDadosManager
from dash.maps import MAPA_SEGMENTOS 

class LeadProspector:
    def __init__(self):
        self.conector_google = ConectorGoogleMaps()
        self.db = BancoDadosManager()
        self.analyzer = SentimentIntensityAnalyzer()

    def calcular_score(self, rating: float, total_reviews: int, sentimento_medio: float) -> float:
        """
        Calcula o Score de Priorização Comercial (0 a 100) combinando:
        - Volume de mercado (Total de avaliações)
        - Reputação do estabelecimento (Rating)
        - Inteligência Semântica / NLP (Sentimento médio das reviews)
        """
        fator_volume = min((total_reviews / 150.0) * 20, 30) 
        fator_rating = rating * 8
        
        score_base = fator_rating + fator_volume
    
        bonus_sentimento = 0.0
        
        if sentimento_medio > 0.4:
            bonus_sentimento = sentimento_medio * 30
            
        elif sentimento_medio < -0.15 and total_reviews > 50:
            bonus_sentimento = abs(sentimento_medio) * 25 
            
        else:
            bonus_sentimento = 10.0

        score_final = score_base + bonus_sentimento
        
        return round(min(max(score_final, 0.0), 100.0), 2)

    def executar_fluxo_prospeccao(self, segmento: str, cidade_regiao: str, limite_leads: int = 5) -> int:
        segmento_limpo = segmento.replace("&", "e").strip()
        cidade_limpa = cidade_regiao.split("(")[0].strip() 

        print(f"\n🚀 [LeadProspector] Iniciando esteira filtrada no Google Maps para '{segmento_limpo}'...")

        config_segmento = MAPA_SEGMENTOS.get(segmento, {"termos_bio": [segmento_limpo]})
        termos_busca_expandidos = config_segmento.get("termos_bio", [segmento_limpo])

        empresas_totais = []
        for termo in termos_busca_expandidos:
            termo_query = termo.replace("&", "e").strip()
            empresas_encontradas = self.conector_google.buscar_empresas_por_tendencia(termo_query, cidade_limpa)
            empresas_totais.extend(empresas_encontradas)

        empresas_unicas = {e['place_id_google']: e for e in empresas_totais if e.get('place_id_google')}.values()
        
        novos_leads_contador = 0

        for empresa in empresas_unicas:
            if novos_leads_contador >= limite_leads:
                print(f"🎯 [LeadProspector] Limite solicitado de {limite_leads} leads atingido com sucesso.")
                break

            if self.db.verificar_existencia_lead(empresa['place_id_google']):
                print(f"⏭️ [Cache] Lead '{empresa['nome_fantasia']}' já existe no Postgres. Pulando...")
                continue 

            print(f"\n📊 Processando inteligência do lead NOVO: {empresa['nome_fantasia']}")
            
            scores_reviews = []
            for review in empresa["reviews_extraidas"]:
                score_sentimento = self.analyzer.polarity_scores(review)
                scores_reviews.append(score_sentimento["compound"])
            
            sentimento_medio = sum(scores_reviews) / len(scores_reviews) if scores_reviews else 0.0
            score_comercial = self.calcular_score(
                rating=empresa["rating_maps"], 
                total_reviews=empresa["total_reviews"], 
                sentimento_medio=sentimento_medio
            )

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
                "tendencia_buzz": f"Busca Expandida: {segmento_limpo}",
                "sentimento_reviews_medio": round(sentimento_medio, 2),
                "score_heuristico": score_comercial
            }

            inserido = self.db.salvar_lead(payload_lead)
            if inserido:
                print(f"✅ [LeadProspector] Novo lead armazenado! Score: {score_comercial}")
                novos_leads_contador += 1

        print(f"\n🏁 [LeadProspector] Varredura finalizada. {novos_leads_contador} novos registros reais inseridos.")
        return novos_leads_contador