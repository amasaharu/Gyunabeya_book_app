import os
import streamlit as st
import yaml
import streamlit_authenticator as stauth
from yaml.loader import SafeLoader

st.title("新規ユーザー登録")

with st.form("register_form"):
    new_username = st.text_input("ユーザーID")
    new_name = st.text_input("表示名")
    new_email = st.text_input("メールアドレス")
    new_password = st.text_input("パスワード", type="password")
    submitted = st.form_submit_button("登録")

if submitted:
    if not new_username or not new_password:
        st.error("ユーザーIDとパスワードは必須です")
    else:
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        CONFIG_PATH = os.path.join(BASE_DIR, "config.yaml")

        # config読み込み
        with open(CONFIG_PATH, "r", encoding="utf-8") as file:
            config = yaml.load(file, Loader=SafeLoader)

        # 重複チェック
        if new_username in config["credentials"]["usernames"]:
            st.error("このユーザーIDはすでに使われています")
        else:
            # パスワードハッシュ化
            hashed_password = stauth.utilities.hasher.Hasher.hash(new_password)

            # ユーザー追加
            config["credentials"]["usernames"][new_username] = {
                "name": new_name,
                "email": new_email,
                "password": hashed_password
            }

            # YAML保存
            with open(CONFIG_PATH, "w", encoding="utf-8") as file:
                yaml.dump(config, file, allow_unicode=True)

            st.success("登録できました！ログイン画面からログインしてください。")