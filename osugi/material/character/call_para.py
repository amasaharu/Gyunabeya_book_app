import streamlit as st
import pandas as pd
from parameter_update import apply_parameter_update

label_map = {
    "attack": "攻撃",
    "defense": "防御",
    "agility": "敏捷",
    "charm": "魅力",
    "intelligence": "知力",
    "concentration": "集中",
    "magic": "魔力",
    "dexterity": "器用",
    "love": "愛情",
    "luck": "運"
}

keys_to_show = list(label_map.keys())

st.title("キャラクター補正シミュレーション")

user_id_text = st.text_input("ユーザーID", "test_user_osugi")
genre_index = st.selectbox("ジャンル番号", list(range(10)), index=1)
status = st.selectbox("読書ステータス", ["未読", "読了", "レビュー済"], index=1)
pages = st.number_input("ページ数", min_value=1, max_value=2000, value=236)

if st.button("補正を適用"):
    before, after = apply_parameter_update(user_id_text, genre_index, status, pages)

    # 必要なキーだけ抽出して日本語ラベルに変換
    filtered_before = {label_map[k]: before.get(k, None) for k in keys_to_show}
    filtered_after = {label_map[k]: after.get(k, None) for k in keys_to_show}

    # DataFrameにまとめて表示
    df = pd.DataFrame({
        "項目": list(filtered_before.keys()),
        "変更前": list(filtered_before.values()),
        "変更後": list(filtered_after.values())
    }).set_index("項目")

    st.success("補正前後キャラパラメータ")
    st.table(df)