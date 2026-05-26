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
    def __init__(self, username, password, usar_proxy=True):
        self.username = username
        self.password = password
        self.cl = Client()
        self.analyzer = SentimentIntensityAnalyzer()
        self.session_file = f"session_{self.username}.json"
        self.logado = False

        # Handler de challenge interativo — resolve SMS/email automaticamente
        self.cl.challenge_code_handler = self._challenge_code_handler

        if usar_proxy:
            self.lista_proxies = [
                "http://iifruwho:2c9kdhxfs5p7@38.154.203.95:5863"
            ]
            proxy_escolhido = random.choice(self.lista_proxies)
            self.cl.set_proxy(proxy_escolhido)
            print(f"Proxy ativado: {proxy_escolhido.split('@')[-1]}")
        else:
            print("Proxy desativado.")

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
                print("Carregando sessão...")
                with open(self.session_file, "r") as f:
                    session_data = json.load(f)
                self.cl.set_settings(session_data)
                self.cl.get_timeline_feed()
                self.logado = True
                print("✅ Sessão carregada!")
                return
            except Exception as e:
                print(f"❌ Sessão expirou: {e}")
                # NUNCA tenta login com senha — só avisa
                raise Exception(
                    "Sessão expirada. Rode o gerar_sessao.py novamente para renovar."
                )
        
        raise Exception(
            "Nenhuma sessão encontrada. Rode o gerar_sessao.py primeiro."
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
        print(f"\nBuscando posts de #{hashtag_alvo}...")
        medias = self.cl.hashtag_medias_recent(hashtag_alvo, amount=quantidade_posts)
        leads_qualificados = []

        for i, media in enumerate(medias):
            user_id = media.user.pk
            username = media.user.username

            print(f"\n[{i+1}/{quantidade_posts}] Processando @{username}...")
            time.sleep(random.randint(4, 7))

            try:
                user_info = self.cl.user_info(user_id)
                bio = user_info.biography.lower().strip() if user_info.biography else ""

                if user_info.is_private:
                    print("-> ❌ Conta privada. Pulando...")
                    continue

                match_localizacao = any(termo in bio for termo in termos_localizacao)
                match_segmento = any(termo in bio for termo in termos_segmento)

                if not (match_localizacao or match_segmento):
                    print("-> ❌ Lead descartado. Bio não condiz com o nicho ou região.")
                    print(f"   Bio analisada: {bio[:60]}...")
                    continue

                seguidores = user_info.follower_count

                if seguidores < min_seguidores:
                    print(f"-> ❌ Lead descartado. Menos de {min_seguidores} seguidores.")
                    continue

                print("-> 🎯 Lead Qualificado! Iniciando extração de métricas...")
                time.sleep(random.randint(3, 5))

                ultimos_posts = self.cl.user_medias(user_id, amount=3)

                total_likes = 0
                total_comments = 0
                todos_scores_sentimento = []

                for post in ultimos_posts:
                    total_likes += post.like_count
                    total_comments += post.comment_count

                    try:
                        time.sleep(random.randint(2, 4))
                        comentarios = self.cl.media_comments(post.id, amount=5)
                        for comp in comentarios:
                            score = self.analyzer.polarity_scores(comp.text)
                            todos_scores_sentimento.append(score["compound"])
                    except Exception:
                        continue

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
                    f"-> ✅ Sucesso! Engajamento: {dados_lead['engajamento_medio']}%"
                    f" | Sentimento: {dados_lead['sentimento_medio']}"
                )

            except Exception as e:
                print(f"Erro no perfil @{username}: {e}")
                if "429" in str(e):
                    print("Rate limit atingido. Parando script.")
                    break

        print("\n--- FUNIL DE PROSPECÇÃO CONCLUÍDO ---")
        print(f"Leads finais qualificados: {len(leads_qualificados)}")
        for lead in leads_qualificados:
            print(
                f"- @{lead['username']}"
                f" | Seg: {lead['seguidores']}"
                f" | Eng: {lead['engajamento_medio']}%"
                f" | Sent: {lead['sentimento_medio']}"
            )

        return leads_qualificados