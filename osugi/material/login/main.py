import streamlit as st

# --- ページルーティング実験 ---
rootchange = st.selectbox(
    '地域',
    ['東京', '大阪']
)

# 地域ごとにメニューを切り替え
if rootchange == '東京':
    st.sidebar.title("メニュー")
    page = st.sidebar.selectbox("ページ選択", ["ホーム", "キャラクター", "本の登録"])

    if page == "ホーム":
        st.write("ログイン成功です。")
        # import home
        # home.show()
    elif page == "キャラクター":
        import character
        character.show()
    elif page == "本の登録":
        import book_registore
        book_registore.show()

elif rootchange == '大阪':
    st.sidebar.title("メニュー")
    page = st.sidebar.selectbox("ページ選択", ["ログイン", "新規登録"])

    if page == "ログイン":
        import login
        login.show()
    elif page == "新規登録":
        import new_regi
        new_regi.show()
