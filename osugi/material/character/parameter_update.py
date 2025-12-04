# import os
# from dotenv import load_dotenv

# 環境変数読み込み
# load_dotenv()
# SUPABASE_URL = os.getenv("SUPABASE_URL")
# SUPABASE_KEY = os.getenv("SUPABASE_KEY")

from supabase import create_client, Client

SUPABASE_URL = "https://wmcppeiutkzrxrgwguvm.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6IndtY3BwZWl1dGt6cnhyZ3dndXZtIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjQ1ODc0MTgsImV4cCI6MjA4MDE2MzQxOH0.nb4J58HBMx5MfFFky1KNstzqzCMiTehfNEVAsp7Egu0"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def apply_parameter_update(user_id_text: str, genre_index: int, status: str, pages: int) -> dict:
    """
    キャラクターのパラメータにジャンル補正を加算する関数
    - user_id_text: ユーザーID文字列
    - genre_index: ジャンル番号
    - status: 読書ステータス ("未読", "読了", "レビュー済")
    - pages: 本のページ数
    """

    # 1. キャラクター取得
    res_char = supabase.table("character").select("*").eq("user_id_text", user_id_text).execute()
    char = res_char.data[0] if res_char.data else {}

    # 2. ジャンル補正値取得
    res_param = supabase.table("parameter").select("*").eq("genre_index", genre_index).execute()
    param = res_param.data[0] if res_param.data else {}

    # ステータス係数
    def get_status_coefficient(status: str) -> float:
        if status == "未読":
            return 0.25
        elif status == "読了":
            return 1.0
        elif status == "レビュー済":
            return 0.5
        else:
            return 0.0

    # ページ数係数
    def get_page_coefficient(p: int) -> float:
        if p < 140:
            return 1.0
        elif 140 <= p < 250:
            return 1.2
        elif 250 <= p < 360:
            return 1.4
        elif 360 <= p < 500:
            return 1.8
        else:
            return 2.4

    status_coef = get_status_coefficient(status)
    page_coef = get_page_coefficient(pages)

    updated = {}
    for key, value in char.items():
        if key in param and isinstance(value, (int, float)) and isinstance(param[key], (int, float)):
            add_value = int(round(param[key] * status_coef * page_coef))
            updated[key] = value + add_value
        else:
            updated[key] = value

        if "evolution" in char and isinstance(char["evolution"], (int, float)):
            updated["evolution"] = char["evolution"] + pages
        else:
            updated["evolution"] = pages  # もし存在しない/Noneなら初期化

    return updated