import streamlit as st
from datetime import datetime, timezone, timedelta
from supabase import create_client, Client

from register_by_barcode_func import barcode_scanner, get_api_book_info

# Supabase呼び出し
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# JSTタイムゾーンを定義
JST = timezone(timedelta(hours=9))

# user_idの取得（セッションステートから取得する想定）
# user_id = st.session_state["user_id"]
user_id = "test_user_01"

# アプリ処理開始
st.title('バーコードで登録')

# 初回のみカメラ起動してISBNを取得
if "isbn_code" not in st.session_state:
    # カメラ映像を配置するプレースホルダーを作成
    camera_placeholder = st.empty()

    # 別ファイルで定義しているbarcode_scanner関数を呼び出してISBNコードを取得
    isbn_code = barcode_scanner(camera_placeholder)

    # 結果表示
    if isbn_code:
        st.session_state["isbn_code"] = isbn_code
        st.success(f'登録する本のISBN: {isbn_code}')
    else:
        st.warning("ISBNを読み取れませんでした。")

        # 再試行ボタン
        if st.button("再試行"):
            isbn_code = barcode_scanner(camera_placeholder)
            if isbn_code:
                st.session_state["isbn_code"] = isbn_code
                st.success(f'登録する本のISBN: {isbn_code}')
            else:
                st.error("再試行してもISBNを読み取れませんでした。")

# ISBNが取得できていれば書誌情報を取得（初回のみ）
if "isbn_code" in st.session_state and "dict_api_book_info" not in st.session_state:
    # 別ファイルで定義しているget_api_book_info関数を呼び出して、ISBNコードを使って書誌情報を取得
    dict_api_book_info = get_api_book_info(st.session_state["isbn_code"])
    st.session_state["dict_api_book_info"] = dict_api_book_info

# 書誌情報がある場合は編集フォームを表示
if "dict_api_book_info" in st.session_state:
    dict_api_book_info = st.session_state["dict_api_book_info"]

    # dict_api_book_info をベースに dict_edited_book_info を作成
    dict_edited_book_info = dict_api_book_info.copy()

    # 編集不要なキー
    fixed_keys = ['isbn', 'pages', 'call_number', 'genre']
    # 表示用ラベル
    dict_book_info_label = {
        "title": "タイトル",
        "title_kana": "タイトルカナ表記",
        "author": "著者",
        "author_kana": "著者カナ表記",
        "publisher": "出版社",
    }

    # 編集可能なキーだけ text_input に展開
    input_keys = []  # ← リセット対象を記録
    for key, value in dict_api_book_info.items():
        if key not in fixed_keys: # text_inputで上書き編集可能にする
            widget_key = f"input_{key}"
            dict_edited_book_info[key] = st.text_input(
                label=dict_book_info_label[key],
                value=str(value),
                key=widget_key
            )
            input_keys.append(widget_key)

    # APIで取得できない追加情報を入力フォームで追加
    dict_edited_book_info["label"] = st.text_input("レーベル", key="input_label")
    dict_edited_book_info["purchase_or_library"] = st.radio("購入/図書館", ["購入", "図書館"], key="input_purchase_or_library")
    dict_edited_book_info["paper_or_digital"] = st.radio("紙/電子書籍", ["紙", "電子書籍"], key="input_paper_or_digital")
    dict_edited_book_info["read_status"] = st.radio("読書状況", ["未読", "読書中", "読了"], key="input_read_status")

    # st.date_input では空欄にできないので「入力する」選択肢を追加
    completed_flag_start = st.checkbox("読み始めた日を入力する")
    if completed_flag_start:
        dict_edited_book_info["started_at"] = st.date_input("読み始めた日", key="input_started_at")
        dict_edited_book_info["started_at"] = dict_edited_book_info["started_at"].isoformat()
    else:
        dict_edited_book_info["started_at"] = None

    # 読了日　st.date_input では空欄にできないので「入力する」選択肢を追加
    completed_flag_complete = st.checkbox("読了日を入力する")
    if completed_flag_complete:
        dict_edited_book_info["completed_at"] = st.date_input("読了日", key="input_completed_at")
        dict_edited_book_info["completed_at"] = dict_edited_book_info["completed_at"].isoformat()
    else:
        dict_edited_book_info["completed_at"] = None

    dict_edited_book_info["review"] = st.text_area("レビュー", key="input_review")
    # 選択肢が「公開する」なら True、そうでなければ False
    dict_edited_book_info["review_published"] = (st.radio("レビュー公開設定", ["公開する", "公開しない"], key="input_review_published") == "公開する")

    # 確認用（完成品では消す）
    st.write("登録内容（完成時は消す）:", dict_edited_book_info)

    # 登録ボタン
    if st.button("登録"):
        dict_edited_book_info['user_id'] = user_id # DB登録用にuser_idを追加
        dict_edited_book_info['created_at'] = datetime.now(JST).isoformat() # 登録日時を追加
        supabase.table("book").insert(dict_edited_book_info).execute()
        st.success("登録しました！")
        st.session_state["registered"] = True

    # 登録成功後だけ「別の本を登録する」ボタンを表示
    if st.session_state.get("registered"):
        if st.button("別の本を登録する"):
            # user_id を保持したまま他のキーを削除
            for key in list(st.session_state.keys()):
                if key not in ["user_id"]:
                    st.session_state.pop(key)
            st.rerun()


