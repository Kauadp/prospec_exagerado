import googlemaps
import streamlit as st
import requests

class ConectorGoogleMaps:
    def __init__(self):
        self.api_key = st.secrets["google"].get("PLACES_API_KEY", "mock_key")
        if self.api_key != "mock_key" and "SUA_CHAVE" not in self.api_key:
            self.mock_mode = False
        else:
            self.mock_mode = True

    def buscar_empresas_por_tendencia(self, termo_busca: str, cidade_regiao: str) -> list[dict]:
        """
        Varre o Google Places (API NEW) buscando estabelecimentos comerciais.
        """
        query_completa = f"{termo_busca} em {cidade_regiao}"
        print(f"🔍 [Google Maps New] Executando Text Search para: '{query_completa}'")

        if self.mock_mode:
            return self._gerar_dados_simulados(termo_busca, cidade_regiao)

        url = "https://places.googleapis.com/v1/places:searchText"
        
        headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": self.api_key,
            "X-Goog-FieldMask": "places.id,places.displayName,places.internationalPhoneNumber,places.websiteUri,places.rating,places.userRatingCount,places.formattedAddress,places.reviews"
        }
        
        payload = {
            "textQuery": query_completa,
            "languageCode": "pt-BR",
            "maxResultCount": 5
        }

        try:
            response = requests.post(url, json=payload, headers=headers)
            
            if response.status_code == 200:
                dados = response.json()
                places = dados.get("places", [])
                
                if not places:
                    print("⚠️ Nenhum lugar encontrado na API New. Ativando mock.")
                    return self._gerar_dados_simulados(termo_busca, cidade_regiao)

                empresas_formatadas = []
                for p in places:
                    reviews_texto = []
                    for rev in p.get('reviews', []):
                        if rev.get('text', {}).get('text'):
                            reviews_texto.append(rev['text']['text'])

                    empresas_formatadas.append({
                        "nome_fantasia": p.get('displayName', {}).get('text', 'Sem nome'),
                        "telefone": p.get('internationalPhoneNumber', 'Não informado'),
                        "site": p.get('websiteUri', 'Não possui site'),
                        "rating_maps": p.get('rating', 0.0),
                        "total_reviews": p.get('userRatingCount', 0),
                        "endereco_completo": p.get('formattedAddress', 'Sem endereço'),
                        "place_id_google": p.get('id'),
                        "reviews_extraidas": [rev.get('text', {}).get('text', '') for rev in p.get('reviews', []) if rev.get('text', {}).get('text')]
                    })
                
                return empresas_formatadas
            else:
                print(f"⚠️ Google Places New retornou erro {response.status_code}: {response.text}. Ativando mock.")
                return self._gerar_dados_simulados(termo_busca, cidade_regiao)

        except Exception as e:
            print(f"❌ Erro de conexão com a API New do Google Maps: {e}")
            return self._gerar_dados_simulados(termo_busca, cidade_regiao)

    def _gerar_dados_simulados(self, termo, cidade) -> list[dict]:
        print("💡 [Google Maps] Injetando dados ricos de simulação regional.")
        return [
            {
                "nome_fantasia": f"Boutique Trend {cidade}",
                "telefone": "(21) 99888-1122" if "Rio" in cidade else "(27) 99888-1122",
                "site": "www.boutiquetrendrj.com.br",
                "rating_maps": 4.6,
                "total_reviews": 112,
                "endereco_completo": f"Av. Copacabana, Rio de Janeiro - RJ",
                "place_id_google": "place_mock_001",
                "reviews_extraidas": [
                    "Amei as roupas inspiradas em cropped fitness, excelente qualidade!",
                    "O atendimento foi um pouco demorado, mas o ambiente é lindo."
                ]
            }
        ]