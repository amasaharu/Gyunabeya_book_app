import streamlit as st
import pandas as pd
from supabase import create_client, Client
import sys

# =================================================================
# 💡 ステータス対応表の定義（0-3の詳細な定義）
# =================================================================

# 数値から日本語へのマップ
STATUS_MAP_FULL = {
    0: "未読",
    1: "読書中",
    2: "読了 (レビュー未登録)",
    3: "読了 (レビュー登録済み)"
}

# 💡 修正: 一覧表示や画面表示で使用するシンプルな日本語マップ
STATUS_MAP_SIMPLE = {
    0: "未読",
    1: "読書中",
    2: "読了", # 2と3はどちらも「読了」として表示
    3: "読了"
}

# 日本語から数値へのマップ (ユーザーの選択肢と対応)
STATUS_REVERSE_MAP = {
    "未読": 0,
    "読書中": 1,
    "読了 (レビュー未登録)": 2,
    "読了 (レビュー登録済み)": 3
}

# --------------------------------------------------------------------------
# Supabase 接続情報の設定
# --------------------------------------------------------------------------

try:
    SUPABASE_URL = st.secrets["SUPABASE_URL"]
    SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
except KeyError:
    st.error("エラー: .streamlit/secrets.toml に 'SUPABASE_URL' または 'SUPABASE_KEY' が記述されていません。ファイルを確認してください。")
    st.stop()


@st.cache_resource
def init_supabase_client():
    """Supabaseクライアントを初期化し、接続を確立する"""
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase: Client = init_supabase_client()


# =================================================================
# データ取得関数
# =================================================================

def fetch_user_books(user_id: str):
    """指定されたユーザーIDに紐づく書籍データを取得する。"""
    columns_to_select = "book_id, isbn, title, author, pages, genre, read_status"
    
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

def fetch_book_detail(book_id: str):
    """指定されたbook_idの詳細データを取得する。"""
    # 💡 prev_status, new_status を取得項目に追加
    columns_to_select = "book_id, user_id, isbn, title, author, pages, genre, publisher, purchase_or_library, paper_or_digital, read_status, review, prev_status, new_status"
    try:
        response = supabase.table("book").select(columns_to_select).eq("book_id", book_id).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        st.error(f"詳細データの取得中にエラーが発生しました: {e}")
        return None


# =================================================================
# UI 定義関数 (画面ごとの表示ロジック)
# =================================================================

def display_book_list(books_data):
    """書籍一覧画面のUIを構築する"""
    st.title("📚 書籍一覧")
    
    df = pd.DataFrame(books_data)
    
    # カラム名を日本語化
    df = df.rename(columns={
        'isbn': 'ISBN', 
        'title': 'タイトル', 
        'author': '著者名', 
        'pages': 'ページ数',
        'genre': 'ジャンル',
        'read_status': '読了ステータス'
    })

    st.subheader(f"取得した書籍 ({len(df)} 冊)")
    
    # ISBNを除外し、カラム幅を調整
    cols = st.columns([3, 2, 1, 1, 1, 0.8])
    cols[0].markdown("**タイトル**")
    cols[1].markdown("**著者名**")
    cols[2].markdown("**ページ数**")
    cols[3].markdown("**ジャンル**")
    cols[4].markdown("**ステータス**")
    cols[5].markdown("**操作**")
    st.markdown("---") 

    for index, row in df.iterrows():
        cols = st.columns([3, 2, 1, 1, 1, 0.8]) 
        
        cols[0].write(row['タイトル'])
        cols[1].write(row['著者名'])
        cols[2].write(row['ページ数'])
        cols[3].write(row['ジャンル'])
        cols[4].write(row['読了ステータス']) 
        
        button_key = f"detail_{row['book_id']}"
        if cols[5].button("詳細", key=button_key):
            st.session_state['selected_book_id'] = row['book_id']
            st.session_state['page'] = 'detail'
            st.rerun() 
        
        st.markdown("---")


def display_book_detail(book_id):
    """書籍詳細画面のUIを構築し、編集・更新処理を行う"""
    st.title("📚 書籍詳細と編集")
    
    # 1. データ取得
    book_detail = fetch_book_detail(book_id)

    if not book_detail:
        st.warning(f"ブックID: {book_id} の詳細情報が見つかりませんでした。")
        if st.button("↩️ 一覧に戻る"):
            st.session_state['page'] = 'list'
            st.rerun()
        return

    # ----------------- 1. 詳細データの整理と表示 -----------------
    st.subheader(book_detail['title'])

    display_data = {
        'タイトル': book_detail['title'],
        '著者名': book_detail['author'],
        'ページ数': book_detail['pages'],
        'ジャンル': book_detail['genre'],
        '出版社': book_detail['publisher'],
        '購入/電子': f"{book_detail['purchase_or_library']} / {book_detail['paper_or_digital']}",
        'レビュー': book_detail['review'] if book_detail['review'] else 'レビュー未登録',
    }

    df_detail = pd.DataFrame.from_dict(display_data, orient='index', columns=['値'])
    st.table(df_detail)


    # ----------------- 2. ステータスの確認・更新 (数値ベース) -----------------
    st.subheader("ステータスの確認・更新")

    # 💡 修正: prev_status (数値) を取得し、シンプルな日本語に変換して表示
    # 現在のステータス = prev_status の値
    current_numerical_status = book_detail.get('prev_status', 0)
    current_japanese_status_simple = STATUS_MAP_SIMPLE.get(current_numerical_status, '不明')
    
    # 詳細画面では、prev_statusの数値と、そのシンプルな日本語を併記
    st.info(f"現在のステータス (prev_status): **{current_japanese_status_simple} ({current_numerical_status})**")


    # 💡 新ステータスの選択肢を日本語にする (詳細な日本語を使用)
    status_options_japanese = list(STATUS_REVERSE_MAP.keys()) 
    
    # new_status (数値) を元に、初期選択肢の日本語（詳細）を取得
    initial_japanese_status = STATUS_MAP_FULL.get(book_detail.get('new_status', 0), '未読')
    
    if initial_japanese_status not in status_options_japanese:
        # マップ外の値の場合の安全策
        initial_japanese_status = '未読' 
        
    initial_index = status_options_japanese.index(initial_japanese_status)

    
    new_japanese_status_full = st.selectbox(
        "新しいステータスを選択してください",
        options=status_options_japanese,
        index=initial_index
    )
    
    # 選択された日本語（詳細）を、データベースに書き込む数値 (0, 1, 2, 3) に変換
    new_numerical_status = STATUS_REVERSE_MAP.get(new_japanese_status_full)
    
    # 💡 修正: read_statusに書き込むシンプルな日本語を決定
    new_japanese_status_simple = STATUS_MAP_SIMPLE.get(new_numerical_status, '不明')


    if st.button("✅ ステータスを更新する"):
        
        try:
            # データベースに書き込むデータ辞書を定義
            update_data = {
                # 1. prev_statusを新しい数値で更新
                "prev_status": new_numerical_status, 
                # 2. new_statusも新しい数値で更新
                "new_status": new_numerical_status,
                # 3. read_status (日本語カラム) をシンプルな日本語で更新 (例: 読了)
                "read_status": new_japanese_status_simple, 
            }
            
            # Supabaseの更新処理
            supabase.table("book") \
                .update(update_data) \
                .eq("book_id", book_id) \
                .execute()
            st.success(f"ステータスが {new_japanese_status_simple} ({new_numerical_status}) に正常に更新されました！")
            
            st.rerun() 
            
        except Exception as e:
            st.error(f"ステータスの更新中にエラーが発生しました: {e}")


    st.markdown("---")
    
    if st.button("↩️ 一覧に戻る"):
        st.session_state['page'] = 'list'
        st.session_state['selected_book_id'] = None 
        st.rerun() 


# =================================================================
# メインロジック（画面切り替え処理）
# =================================================================

st.set_page_config(layout="wide")

# session_state の初期化
if 'page' not in st.session_state:
    st.session_state['page'] = 'list'

if 'user_id' not in st.session_state:
    st.session_state['user_id'] = ""

current_user_id = st.text_input(
    "データを取得するユーザーIDを入力してください", 
    value=st.session_state['user_id'], 
    key="user_id_input"
)
st.session_state['user_id'] = current_user_id


# === 画面の切り替え処理 ===

if st.session_state['page'] == 'list':
    # 一覧画面の表示
    if current_user_id:
        books_data = fetch_user_books(current_user_id)
        if books_data:
            display_book_list(books_data)
        elif books_data is not None:
            st.warning(f"ユーザーID: **{current_user_id}** に紐づく書籍データは見つかりませんでした。")

elif st.session_state['page'] == 'detail':
    # 詳細画面の表示
    if 'selected_book_id' in st.session_state and st.session_state['selected_book_id']:
        display_book_detail(st.session_state['selected_book_id'])
    else:
        # book_id がない場合は一覧に戻す
        st.session_state['page'] = 'list'
        st.rerun()