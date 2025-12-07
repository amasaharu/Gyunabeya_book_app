import streamlit as st
import pandas as pd
from supabase import create_client, Client
import os
import sys

# 【注意】ここをご自身の情報に置き換えてください
SUPABASE_URL = "https://wmcppeiutkzrxrgwguvm.supabase.co" 
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6IndtY3BwZWl1dGt6cnhyZ3dndXZtIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NDU4NzQxOCwiZXhwIjoyMDgwMTYzNDE4fQ.RnAl8nkeMuLXUptiaznC2AKfgdR7XN_nhp78dH59saA" 

if SUPABASE_URL == "YOUR_SUPABASE_URL" or SUPABASE_KEY == "YOUR_SUPABASE_KEY":
    st.error("エラー: Supabase接続情報 (URL および KEY) をコード内に記述してください。")
    st.stop()


@st.cache_resource
def init_supabase_client():
    """Supabaseクライアントを初期化し、接続を確立する"""
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase: Client = init_supabase_client()


def fetch_user_books(user_id: str):
    """
    指定されたユーザーIDに紐づく書籍データをSupabaseから取得する。
    """
    
    # book_id を含めた必要なカラムを選択
    columns_to_select = "book_id, isbn, title, author, pages, genre"
    
    st.info(f"📚 ユーザーID: **{user_id}** の書籍データを取得中...")

    try:
        response = supabase.table("book") \
            .select(columns_to_select) \
            .eq("user_id", user_id) \
            .execute()

        return response.data

    except Exception as e:
        st.error(f"データの取得中にエラーが発生しました: {e}")
        return None

# =================================================================
# Streamlit UI
# =================================================================

st.set_page_config(layout="wide")
st.title("📚 書籍一覧")

# ユーザーIDの手入力運用
if 'user_id' not in st.session_state:
    st.session_state['user_id'] = ""

current_user_id = st.text_input(
    "データを取得するユーザーIDを入力してください", 
    value=st.session_state['user_id'], 
    key="user_id_input"
)
st.session_state['user_id'] = current_user_id


if current_user_id:
    books_data = fetch_user_books(current_user_id)

    if books_data:
        df = pd.DataFrame(books_data)
        
        # カラム名を日本語化
        df = df.rename(columns={
            'isbn': 'ISBN', 
            'title': 'タイトル', 
            'author': '著者名', 
            'pages': 'ページ数',
            'genre': 'ジャンル'
        })

        st.subheader(f"取得した書籍 ({len(df)} 冊)")
        
        # 💡 修正箇所：各行に「詳細」ボタンを表示する
        
        # データをイテレートして、一行ずつ表示とボタンを配置
        for index, row in df.iterrows():
            col1, col2, col3, col4, col5, col6, col7 = st.columns([1, 2, 2, 1, 1, 1, 0.8])
            
            # 各カラムのデータを表示
            col1.write(row['ISBN'])
            col2.write(row['タイトル'])
            col3.write(row['著者名'])
            col4.write(row['ページ数'])
            col5.write(row['ジャンル'])
            
            # 💡 遷移ボタンを配置
            button_key = f"detail_{row['book_id']}"
            if col7.button("詳細", key=button_key):
                # 選択された book_id をセッションステートに保存
                st.session_state['selected_book_id'] = books_data[index]['book_id']
                
                # 詳細ページへ遷移
                st.switch_page("pages/detail_edit.py")
            
            # 区切り線
            st.markdown("---")
            
    elif books_data is not None:
        st.warning(f"ユーザーID: **{current_user_id}** に紐づく書籍データは見つかりませんでした。")