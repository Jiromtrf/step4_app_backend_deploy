import os
from dotenv import load_dotenv

load_dotenv()

SERVER_URL = os.environ["SERVER_URL"]
DATABASE = os.environ["DATABASE"]
USER_NAME = os.environ["USER_NAME"]
PASSWORD = os.environ["PASSWORD"]
SERVER_PORT = os.environ["SERVER_PORT"]
SSL_CA_PATH = os.environ.get("SSL_CA_PATH", "")

DATABASE_URL = f"mysql+pymysql://{USER_NAME}:{PASSWORD}@{SERVER_URL}:{SERVER_PORT}/{DATABASE}?charset=utf8"

# SSLを使用する場合
if SSL_CA_PATH:
    DATABASE_URL += f"&ssl_ca={SSL_CA_PATH}"

# セキュリティ設定
SECRET_KEY = os.environ.get("NEXTAUTH_SECRET", "fallback_secret_key")  # 環境変数がない場合はデフォルト値
ALGORITHM = "HS256"  # JWTの署名アルゴリズム

# CORS設定（必要に応じて追加）
ALLOWED_ORIGINS = os.environ.get("ALLOWED_ORIGINS", "*").split(",")  # 環境変数からカンマ区切りで取得