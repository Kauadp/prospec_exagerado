import json
import os
from instagrapi import Client
import streamlit as st

USERNAME = st.secrets["account"]["USERNAME"]
PASSWORD = st.secrets["account"].get("PASSWORD") 
SESSION_FILE = f"session_{USERNAME}.json"

def challenge_code_handler(username, choice):
    """
    Interceptor de segurança: se o Instagram pedir código por SMS ou E-mail,
    o script pausa e deixa você digitar direto no terminal.
    """
    print(f"\n⚠️  O INSTAGRAM EXIGIU VERIFICAÇÃO DE SEGURANÇA PARA @{username}")
    print(f"   Tipo de envio solicitado: {choice}")
    code = input("   👉 Digite o código de verificação recebido: ").strip()
    return code

cl = Client()

cl.challenge_code_handler = challenge_code_handler

cl.set_device({
    "app_version": "269.0.0.18.75",
    "android_version": 26,
    "android_release": "8.0.0",
    "dpi": "480dpi",
    "resolution": "1080x1920",
    "manufacturer": "Google",
    "device": "Pixel 8 Pro",
    "model": "Pixel 8 Pro",
    "cpu": "qcom",
    "version_code": "314665256"
})

PROXY = "http://iifruwho:2c9kdhxfs5p7@38.154.203.95:5863"

print("🚀 Iniciando fluxo de autenticação...")

try:
    print(f"🔐 Tentando logar na conta: @{USERNAME}...")
    cl.set_proxy(PROXY)
    print(f"Proxy ativado para a geração da sessão: {PROXY.split('@')[-1]}")
    cl.login(USERNAME, PASSWORD)
    
    cl.dump_settings(SESSION_FILE)
    print(f"\n✅ SUCESSO! Sessão estruturada gerada e salva em: {SESSION_FILE}")
    print("Agora o seu scrapping.py conseguirá rodar usando essa credencial sem disparar blocks.")

except Exception as e:
    print(f"\n❌ Erro crítico ao tentar autenticar: {e}")