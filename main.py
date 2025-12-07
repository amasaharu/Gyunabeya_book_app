import os
import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader

# config.yaml の絶対パス
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(BASE_DIR, "config.yaml")

# 読み込み
with open(CONFIG_PATH, "r", encoding="utf-8") as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    credentials=config['credentials'],
    cookie_name=config['cookie']['name'],
    cookie_key=config['cookie']['key'],
    cookie_expiry_days=config['cookie']['expiry_days'],
)

# ログインフォーム
authenticator.login(
    location="main",
    fields={
        "Form name": "ログイン",
        "Username": "ユーザーID",
        "Password": "パスワード",
        "Login": "ログイン"
    }
)

status = st.session_state.get("authentication_status")
if status:
    # ログイン成功時にユーザー情報をセッションに保持
    st.session_state["user_id"] = st.session_state.get("username")  # ユーザーID
    st.session_state["user_name"] = st.session_state.get("name")     # 表示名

if status:
    with st.sidebar:
        st.markdown(f'## ようこそ、 *{st.session_state.get("name", "")}* さん')
        authenticator.logout('ログアウト', 'sidebar')
        st.divider()
    st.write('# ログインしました!')
elif status is False:
    st.error('ユーザーIDかパスワードが間違っています')
else:
    st.warning('ユーザーIDとパスワード、入力できましたか？')