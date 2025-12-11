import streamlit as st
from supabase import create_client, Client

st.set_page_config(page_title="Book App", layout="centered")

# --- CSS ---
st.markdown("""
<style>
.center-buttons {
    display: flex;
    justify-content: center;
    gap: 40px;
    margin-top: 20px;
}
.custom-btn {
    background-color: #d1a64f;
    color: black !important;
    padding: 14px 32px;
    border-radius: 12px;
    font-size: 20px;
    font-weight: bold;
    text-decoration: none !important;
    display: inline-flex;
    align-items: center;
    box-shadow: 2px 2px 6px rgba(0,0,0,0.3);
}
.custom-btn:hover {
    background-color: #c0903f;
}
.icon { margin-right: 8px; }

.reading-title {
    text-align: center;
    margin-top: 20px;
    font-size: 28px;
    font-weight: bold;
}

@media (max-width: 600px) {
    .reading-title { font-size: 20px; }
}

.metric-wrapper { text-align: center; margin-top: 20px; font-size: 20px; }

.metric-flex {
    display: flex;
    justify-content: center;
    gap: 60px;
}

@media (max-width: 600px) {
    .metric-flex { flex-direction: column; gap: 20px; }
}

.metric-value {
    font-size: 32px;
    font-weight: bold;
    margin-top: -5px;
}
</style>
""", unsafe_allow_html=True)


# --- ボタン横並び ---
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("📝 書籍登録", use_container_width=True):
        st.switch_page("contents/register_by_barcode.py")

with col2:
    if st.button("📚 書籍一覧", use_container_width=True):
        st.switch_page("contents/book_ichiran.py")

with col3:
    if st.button("🥚 キャラクター", use_container_width=True):
        st.switch_page("contents/character.py")

# --- Supabase 接続 ---
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ======================================================
# 🟡 ログイン中ユーザー
# ======================================================
user_id = st.session_state.get("username")  # streamlit-authenticator のログインID
user_name = st.session_state.get("name", "あなた")


# ======================================================
# 🟢 読書データ取得（冊数：全件 / ページ数：読了のみ）
# ======================================================
def get_book_stats(user_id):
    if user_id is None:
        return 0, 0

    # --- 全冊数 ---
    result_all = (
        supabase.table("book")
        .select("*")
        .eq("user_id", user_id)
        .execute()
    )
    books_count = len(result_all.data) if result_all.data else 0

    # --- 読了のページ数 ---
    result_read = (
        supabase.table("book")
        .select("pages")
        .eq("user_id", user_id)
        .eq("read_status", "読了")       # ★ 読了のみ
        .execute()
    )

    if not result_read.data:
        return books_count, 0

    pages_sum = sum([row["pages"] for row in result_read.data])
    return books_count, pages_sum


# --- 冊数とページ数を取得 ---
books_count, pages_sum = get_book_stats(user_id)

# --- タイトル ---
st.markdown(
    f"""
<div class="reading-title">
📊 {user_name} さんの読書データ
</div>
""",
    unsafe_allow_html=True
)

# --- メトリクス表示（※インデントなし！HTML崩れ防止） ---
html = f"""
<div class="metric-wrapper">
<div class="metric-flex">

<div>
登録した冊数
<div class="metric-value">{books_count} 冊</div>
</div>

<div>
読了総ページ数
<div class="metric-value">{pages_sum} ページ</div>
</div>

</div>
</div>
"""

st.markdown(html, unsafe_allow_html=True)