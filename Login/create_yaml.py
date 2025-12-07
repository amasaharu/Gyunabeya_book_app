import os
import csv
import yaml
import bcrypt

BASE_DIR = os.path.dirname(__file__)
users_csv_path = os.path.join(BASE_DIR, "user_info.csv")
config_yaml_path = os.path.join(BASE_DIR, "config.yaml")

print("CSV file path:", users_csv_path)
print("YAML file path:", config_yaml_path)

# CSV 読み込み
with open(users_csv_path, "r", encoding="utf-8") as f:
    csvreader = csv.DictReader(f)
    users = list(csvreader)

print("number of users:", len(users))
if len(users) == 0:
    print("警告: user_info.csv にユーザーがいません。中身を確認してください。")

# YAML 読み込み（None 対策）
with open(config_yaml_path, "r", encoding="utf-8") as f:
    yaml_data = yaml.safe_load(f) or {}

# credentials 初期化
yaml_data.setdefault("credentials", {})
yaml_data["credentials"].setdefault("usernames", {})

# CSV -> usernames dict (bcryptでハッシュ)
users_dict = {}
for user in users:
    raw_pw = user.get("password", "")
    if raw_pw == "":
        print(f"警告: id={user.get('id')} の password が空です。")
    # bcrypt ハッシュ化（デフォルトで $2b$... 形式）
    hashed = bcrypt.hashpw(raw_pw.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    users_dict[user["id"]] = {
        "name": user.get("name", ""),
        "password": hashed,
        "email": user.get("email", ""),
    }

# YAML に反映して保存
yaml_data["credentials"]["usernames"] = users_dict

with open(config_yaml_path, "w", encoding="utf-8") as f:
    yaml.dump(yaml_data, f, allow_unicode=True, sort_keys=False)

print("YAML 書き込み完了！")
