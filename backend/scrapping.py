import json
import os
import time
import random
import logging
from instagrapi import Client
from LeIA import SentimentIntensityAnalyzer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class InstagramProspector:
    def __init__(self, username, password, usar_proxy=False):
        self.username = username
        self.password = password
        self.cl = Client()
        self.analyzer = SentimentIntensityAnalyzer()
        self.session_file = f"session_{self.username}.json"
        self.logado = False

        self.cl.challenge_code_handler = self._challenge_code_handler

        self.cl.set_device({
            "app_version": "269.0.0.18.75",
            "android_version": 26,
            "android_release": "8.0.0",
            "dpi": "480dpi",
            "resolution": "1080x1920",
            "manufacturer": "Google",
            "device": "Pixel 8 Pro",
            "model": "Pixel 8 Pro",
            "cpu": "com",
            "version_code": "314665256"
        })

        if usar_proxy:
            self.lista_proxies = [
                "http://iifruwho:2c9kdhxfs5p7@38.154.203.95:5863"
            ]
            proxy_escolhido = random.choice(self.lista_proxies)
            self.cl.set_proxy(proxy_escolhido)
            print(f"Proxy ativado: {proxy_escolhido.split('@')[-1]}")
        else:
            print("Proxy desativado. Usando conexão local.")

    def _challenge_code_handler(self, username, choice):
        """Resolve challenges de verificação de forma interativa."""
        print(f"\n⚠️  Instagram exigiu verificação para @{username}")
        print(f"   Tipo de verificação: {choice}")
        code = input("   Digite o código recebido por SMS ou e-mail: ").strip()
        return code

    def login(self):
        if self.logado:
            return

        if os.path.exists(self.session_file):
            try:
                print(f"🔄 Carregando cookies e configurações de {self.session_file}...")
                
                # 🔥 O método correto e estável para carregar as configurações salvas pelo auth.py
                self.cl.load_settings(self.session_file)
                
                # Faz uma chamada leve no feed para testar se a sessão ainda está de pé
                self.cl.get_timeline_feed()
                self.logado = True
                print("✅ Sessão carregada e validada com sucesso!")
                return
            except Exception as e:
                print(f"❌ Sessão expirou ou falhou na validação: {e}")
                raise Exception(
                    f"Sessão expirada. Rode o auth.py novamente para renovar os cookies de @{self.username}."
                )
        
        raise Exception(
            f"Nenhuma sessão encontrada para @{self.username}. Rode o auth.py primeiro para gerar o arquivo."
        )

    def buscar_leads(
        self,
        hashtag_alvo,
        termos_localizacao,
        termos_segmento,
        quantidade_posts=10,
        min_seguidores=1000,
    ):
        self.login()
        print(f"\n📥 Buscando posts recentes de #{hashtag_alvo}...")
        medias = self.cl.hashtag_medias_recent(hashtag_alvo, amount=quantidade_posts)
        leads_qualificados = []

        for i, media in enumerate(medias):
            user_id = media.user.pk
            username = media.user.username

            print(f"\n🔍 [{i+1}/{len(medias)}] Analisando perfil: @{username}...")
            
            time.sleep(random.uniform(5.0, 9.0))

            try:
                user_info = self.cl.user_info(user_id)
                bio = user_info.biography.lower().strip() if user_info.biography else ""

                if user_info.is_private:
                    print("-> ❌ Conta privada. Pulando...")
                    continue

                # Normaliza a verificação (case-insensitive)
                match_localizacao = any(termo.lower() in bio for termo in termos_localizacao)
                match_segmento = any(termo.lower() in bio for termo in termos_segmento)

                if not (match_localizacao or match_segmento):
                    print("-> ❌ Lead descartado. Bio não condiz com o nicho ou região do evento.")
                    continue

                seguidores = user_info.follower_count
                if seguidores < min_seguidores:
                    print(f"-> ❌ Lead descartado. Filtro de seguidores ({seguidores} < {min_seguidores}).")
                    continue

                print("🎯 LEAD QUALIFICADO! Buscando métricas de engajamento e sentimento...")
                time.sleep(random.uniform(4.0, 7.0))

                ultimos_posts = self.cl.user_medias(user_id, amount=3)

                total_likes = 0
                total_comments = 0
                todos_scores_sentimento = []

                for post in ultimos_posts:
                    total_likes += post.like_count
                    total_comments += post.comment_count

                    try:
                        time.sleep(random.uniform(3.0, 5.0))
                        comentarios = self.cl.media_comments(post.id, amount=5)
                        for comp in comentarios:
                            score = self.analyzer.polarity_scores(comp.text)
                            todos_scores_sentimento.append(score["compound"])
                    except Exception:
                        continue # Se der erro em um comentário específico, não quebra a esteira

                num_posts = len(ultimos_posts) if ultimos_posts else 1
                engajamento = (
                    ((total_likes + total_comments) / num_posts) / seguidores
                    if seguidores > 0
                    else 0
                )
                sentimento_medio = (
                    sum(todos_scores_sentimento) / len(todos_scores_sentimento)
                    if todos_scores_sentimento
                    else 0.0
                )

                dados_lead = {
                    "username": username,
                    "seguidores": seguidores,
                    "engajamento_medio": round(engajamento * 100, 2),
                    "sentimento_medio": round(sentimento_medio, 2),
                    "bio": user_info.biography.replace("\n", " ") if user_info.biography else "",
                }
                leads_qualificados.append(dados_lead)
                print(
                    f"->  Sucesso! Engajamento: {dados_lead['engajamento_medio']}%"
                    f" | Sentimento: {dados_lead['sentimento_medio']}"
                )

            except Exception as e:
                print(f"❌ Erro ao processar perfil @{username}: {e}")
                if "429" in str(e):
                    print("🚨 [CRÍTICO] Rate limit atingido no Instagram. Pausando execução por segurança.")
                    break

        print("\n🏁 --- FUNIL DE PROSPECÇÃO CONCLUÍDO ---")
        print(f"Leads finais qualificados e validados: {len(leads_qualificados)}")
        return leads_qualificados