import streamlit as st
import new_regi  # ← ファイル名に合わせて修正

from supabase import create_client, Client

# Supabase設定
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

st.markdown("""
<style>

/* サイドバー本体（焼け焦げた古紙テクスチャ） */
section[data-testid="stSidebar"] > div:first-child {
    position: relative !important;
    overflow: hidden !important;

    /* 焼け焦げた古紙テクスチャ（差し替えOK） */
    background-image: url("https://wmcppeiutkzrxrgwguvm.supabase.co/storage/v1/object/public/material/texture_1.png");
    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;

    border-radius: 14px;
}

/* 内側ぼわぼわ光（柔らかい呼吸） */
section[data-testid="stSidebar"] > div:first-child::before {
    content: "";
    position: absolute;
    top: -8px; left: -8px;
    width: calc(100% + 16px);
    height: calc(100% + 16px);

    border: 8px solid rgba(255, 230, 150, 0.25);
    border-radius: 18px;

    box-shadow:
        0 0 20px rgba(255, 240, 180, 0.25),
        inset 0 0 20px rgba(255, 240, 180, 0.2);

    animation: softPulse 4s ease-in-out infinite;
    pointer-events: none;
    z-index: 1;
}

/* 外側の淡い光（控えめで上品） */
section[data-testid="stSidebar"] > div:first-child::after {
    content: "";
    position: absolute;
    top: -12px; left: -12px;
    width: calc(100% + 24px);
    height: calc(100% + 24px);

    border: 4px solid rgba(255, 240, 180, 0.15);
    border-radius: 20px;

    box-shadow:
        0 0 30px rgba(255, 240, 180, 0.25);

    pointer-events: none;
    z-index: 0;
}

/* 内側の柔らかい呼吸アニメーション */
@keyframes softPulse {
    0% {
        border-color: rgba(255, 230, 150, 0.25);
        box-shadow:
            0 0 20px rgba(255, 240, 180, 0.25),
            inset 0 0 20px rgba(255, 240, 180, 0.2);
    }
    50% {
        border-color: rgba(255, 240, 180, 0.6);
        box-shadow:
            0 0 40px rgba(255, 240, 180, 0.6),
            inset 0 0 35px rgba(255, 240, 180, 0.4);
    }
    100% {
        border-color: rgba(255, 230, 150, 0.25);
        box-shadow:
            0 0 20px rgba(255, 240, 180, 0.25),
            inset 0 0 20px rgba(255, 240, 180, 0.2);
    }
}

/* ヘッダー */
[data-testid="stHeader"] {
    background: transparent !important;
    color: #333;
    text-shadow: 1px 1px 2px rgba(255,255,255,0.6);
}

</style>
""", unsafe_allow_html=True)


bg_url = "https://wmcppeiutkzrxrgwguvm.supabase.co/storage/v1/object/public/material/character_background_7.PNG"
st.markdown(f"""
<style>
.stApp {{
    background-image: url("{bg_url}");
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
}}
</style>
""", unsafe_allow_html=True)

users = {"osugi": "tes"}
users = {"osugi": "tes"}

# --- セッション初期化 ---
if "logincheck" not in st.session_state:
    st.session_state.logincheck = 0  # 0=未ログイン, 1=成功
if "page_state" not in st.session_state:
    st.session_state.page_state = "login"  # login or new_regi

# --- ログインページ ---
if st.session_state.page_state == "login":
    st.title("ログインページ")

    if st.session_state.logincheck == 0:
        user_id = st.text_input("ユーザーID")
        password = st.text_input("パスワード", type="password")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("ログイン"):
                if user_id in users and users[user_id] == password:
                    st.session_state.logincheck = 1
                    st.success("ログイン成功！")
                    st.rerun()
                else:
                    st.error("ユーザーIDまたはパスワードが違います")
        with col2:
            if st.button("新規登録へ"):
                st.session_state.page_state = "new_regi"
                st.rerun()

# --- 新規登録ページ ---
elif st.session_state.page_state == "new_regi":
    new_regi.show()
#    if st.button("ログインページへ戻る"):
#        st.session_state.page_state = "login"
#        st.rerun()

# --- ログイン後のメニュー ---
if st.session_state.logincheck == 1 and st.session_state.page_state == "login":
    st.sidebar.title("メニュー")
    page = st.sidebar.selectbox("ページ選択", ["ホーム", "キャラクター", "本の登録", "ログアウト"])

    if page == "ホーム":
        st.write("ログイン成功です。")
    elif page == "キャラクター":
        import character
        character.show()
    elif page == "本の登録":
        import book_registore
        book_registore.show()
    elif page == "ログアウト":
        st.session_state.logincheck = 0
        st.warning("ログアウトしました。")
        st.rerun()