from instagrapi import Client
import json
import streamlit as st

USERNAME = st.secrets["account"]["USERNAME"]
SESSION_ID = st.secrets["account"]["SESSION_ID"]
DS_USER_ID = st.secrets["account"]["DS_USER_ID"]

cl = Client()
# Define device antes de setar a sessão
cl.set_settings({
    "device_settings": {
        "app_version": "269.0.0.18.75",
        "android_version": 26,
        "android_release": "8.0.0",
        "dpi": "480dpi",
        "resolution": "1080x1920",
        "manufacturer": "Google",
        "device": "Pixel 8 Pro",
        "model": "Pixel 8 Pro",
        "cpu": "qcom",
        "version_code": "314665256",
    },
    "cookies": {
        "sessionid": SESSION_ID,
        "ds_user_id": DS_USER_ID,
    }
})

cl.login_by_sessionid(SESSION_ID)

with open(f"session_{USERNAME}.json", "w") as f:
    json.dump(cl.get_settings(), f)

print("✅ Sessão salva!")