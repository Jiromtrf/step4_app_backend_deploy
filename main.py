from fastapi import FastAPI, Request, HTTPException, Query
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from fastapi.openapi.utils import get_openapi

from routers.auth_router import router as auth_router
from routers.user_router import router as user_router
from routers.team_router import router as team_router
from routers.quiz_router import router as quiz_router
from db.config import ALLOWED_ORIGINS
import logging

from slack_utils import send_message_to_slack, get_messages_from_slack
from pydantic import BaseModel
from typing import List, Optional
import sqlite3

app = FastAPI()

# ログの設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# CORSミドルウェアの設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# セキュリティスキームの定義
bearer_scheme = HTTPBearer()

# ルーターの登録
app.include_router(auth_router)
app.include_router(user_router)
app.include_router(team_router)
app.include_router(quiz_router)

# OpenAPI スキーマのカスタマイズ
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Your API",
        version="1.0.0",
        description="API documentation",
        routes=app.routes,
    )
    print("OpenAPI schema before adding security schemes:", openapi_schema)  # デバッグ用

    # セキュリティスキームの追加
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }
    print("SecuritySchemes added:", openapi_schema["components"]["securitySchemes"])  # デバッグ用

    # 全エンドポイントにセキュリティスキームを適用
    for path in openapi_schema["paths"]:
        for method in openapi_schema["paths"][path]:
            openapi_schema["paths"][path][method]["security"] = [{"BearerAuth": []}]
    print("Security applied to all paths")  # デバッグ用

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )


# メッセージ送信のデータ形式を定義
class Message(BaseModel):
    text: str

class Reaction(BaseModel):
    channel: str
    timestamp: str
    emoji: str

class Reply(BaseModel):
    channel: str
    thread_ts: str
    text: str

# SQLiteデータベースのパス
DATABASE_PATH = "database/team_building.db"

# データベースに接続し、クエリを実行するヘルパー関数
def query_database(query: str, params: tuple) -> List[dict]:
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

# Slack関連のエンドポイント
@app.post("/send_message/")
async def send_message(message: Message):
    print("Received text:", message.text)  # 受け取ったテキストを表示
    response = send_message_to_slack(message.text)
    if not response.get("ok"):
        raise HTTPException(status_code=400, detail=response.get("error", "Unknown error"))
    return {"status": "Message sent", "data": response}

@app.get("/get_messages/")
async def get_messages():
    print("Request received at /get_messages")  # リクエスト受信の確認
    response = get_messages_from_slack()
    if not response.get("status") == "ok":
        error_detail = response.get("message", "Unknown error")
        print("Error detail:", error_detail)  # エラーメッセージを出力
        raise HTTPException(status_code=400, detail=error_detail)
    print("Response data:", response["data"])  # 取得したデータの確認
    return {"status": "Messages retrieved", "data": response["data"]}

@app.post("/add_reaction/")
async def add_reaction(reaction: Reaction):
    print("Received Reaction Data:", reaction)  # 受け取ったデータをログに表示
    response = add_reaction_to_message(reaction.channel, reaction.timestamp, reaction.emoji)
    if not response.get("ok"):
        raise HTTPException(status_code=400, detail=response.get("error", "Unknown error"))
    return {"status": "Reaction added", "data": response}


@app.post("/send_reply/")
async def send_reply(reply: Reply):
    response = reply_to_message(reply.channel, reply.thread_ts, reply.text)
    if not response.get("ok"):
        raise HTTPException(status_code=400, detail=response.get("error", "Unknown error"))
    return {"status": "Reply sent", "data": response}

# ユーザー検索エンドポイント
@app.get("/users/")
def search_users(name: Optional[str] = Query(None), expertise: Optional[str] = Query(None), desiredSkills: Optional[str] = Query(None)):
    query = "SELECT * FROM UserSkills WHERE 1=1"
    params = []

    # 各条件をANDでつなげる
    if name:
        query += " AND Name LIKE ?"
        params.append(f"%{name}%")
    if expertise:
        query += " AND Expertise LIKE ?"
        params.append(f"%{expertise}%")
    if desiredSkills:
        query += " AND DesiredSkills LIKE ?"
        params.append(f"%{desiredSkills}%")
    
    return query_database(query, tuple(params))

# Slackイベント処理エンドポイント(実装までコメントアウト)
#app.add_route("/slack/events", slack_events, methods=["POST"])