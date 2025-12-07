import streamlit as st
from supabase import create_client, Client

def generate_monster_prompt(user_id: str) -> str:
    """
    指定したユーザーIDのステータスと species_mapping を使って
    モンスター生成用プロンプトを返す関数
    """

    # Supabaseクライアント生成（secretsから取得）
    SUPABASE_URL = st.secrets["SUPABASE_URL"]
    SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

    status_keys = ["attack", "defense", "agility", "charm", "intelligence","concentration","magic","dexterity","love","luck"]  # 必要な列を列挙

    """
    # テスト用のデータセット
    row = {
    "attack": 60,
    "defense": 80,
    "agility": 160,
    "charm": 60,
    "intelligence": 510,
    "concentration": 505,
    "magic": 520,
    "dexterity": 150,
    "love": 70,
    "luck": 65
    }
    """

    # characterテーブルから対象ユーザーのステータスを取得
    row = supabase.table("character").select(",".join(status_keys)).eq("user_id_text", user_id).execute().data[0]


    # species_mapping を一式取得
    mapping_rows = supabase.table("species_mapping").select("*").execute().data

    def within_20percent(a, b):
        return abs(a - b) / max(a, b) <= 0.2

    # ステータスソート
    sorted_params = sorted(row.items(), key=lambda x: x[1], reverse=True)
    top1, top2, top3 = sorted_params[0], sorted_params[1], sorted_params[2]
    top1_name, top2_name, top3_name = top1[0], top2[0], top3[0]

    # 種族判定
    chosen = None
    if within_20percent(top1[1], top2[1]):
        for r in mapping_rows:
            param_list = r["parameter"].split("_")
            if len(param_list) == 2 and {top1_name, top2_name} <= set(param_list):
                chosen = r
                break

    if not chosen and within_20percent(top1[1], top2[1]) and within_20percent(top1[1], top3[1]):
        for r in mapping_rows:
            param_list = r["parameter"].split("_")
            if len(param_list) == 3 and {top1_name, top2_name, top3_name} <= set(param_list):
                chosen = r
                break

    if not chosen:
        chosen = next(r for r in mapping_rows if r["parameter"] == top1_name)

    species, appearance, battle_style = chosen["species"], chosen["Appearance"], chosen["battle_style"]
    type_val = next(r["type"] for r in mapping_rows if r["parameter"] == top2_name)
    color_val = next(r["color"] for r in mapping_rows if r["parameter"] == top3_name)

    # 進化段階判定
    if top1[1] >= 500:
        stage = chosen["legend"]
        stage_design = "荘厳で厳か、畏怖と尊厳を放つ超越的で崇高なデザインにしてください。"
    elif top1[1] >= 150:
        stage = chosen["adult"]
        stage_design = "成熟した風格、自信と落ち着きを兼ね備えた雰囲気を持つデザインにしてください。"
    else:
        stage = chosen["child"]
        stage_design = "愛嬌があって可愛らしいデザインにしてください。"

    # 英語キーを日本語に変換する辞書
    status_labels = {
    "attack": "攻撃",
    "defense": "防御",
    "agility": "素早さ",
    "charm": "魅力",
    "intelligence": "知力",
    "concentration": "集中",
    "magic": "魔力",
    "dexterity": "器用さ",
    "love": "愛",
    "luck": "運"
    }
    
    # ステータス整形
    status_text = "\n".join([
        f"{status_labels.get(k, k)}: {v}"  # 辞書にあれば日本語、なければそのまま
        for k, v in row.items()
    ])

    # プロンプト生成
    prompt = f"""
あなたはゲームデザイナーです。モンスターデザインを担当しています。
以下の指示に従ってモンスターを1体作成してください。
出力はモンスターの画像のみで、パラメータなどの情報は記載しないでください。
背景はモンスターに合わせてください。
このキャラクターの能力値は以下の通りです：
{status_text}

種族：{species}（{appearance}、{battle_style}）。({species})に複数の値がある場合は、パラメータ値の特徴をくみ取って1つ選んでください。
タイプ：{type_val}。({type_val})に複数の値がある場合は、パラメータ値の特徴をくみ取って組み合わせるか、1つ選んでください。
色：主な色は{type_val}から連想する色を選んでください。({type_val})に複数の値がある場合は、パラメータ値の特徴をくみ取ってデザインしてください。またモンスターの体全体の30%程度に{color_val}を使ってください。
ベースデザイン：{stage}。{stage}に複数の値がある場合は、1つ選んでください。
全体的なデザインの指示：{stage_design}
"""
    return prompt.strip()