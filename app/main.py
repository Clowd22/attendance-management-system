# =============================================================================
# アプリケーションのエントリポイント
# -----------------------------------------------------------------------------
# uvicorn app.main:app で起動される。
# ・セッション管理のミドルウェア設定
# ・ルーターの登録
# ・エラーハンドラ（403 / 404）
# を行う。
# =============================================================================
from fastapi import FastAPI, Request
from starlette.middleware.sessions import SessionMiddleware

from app.api.routes import auth, home
from app.core.config import get_settings
from app.core.templates import templates

# 設定を読み込む
settings = get_settings()

# FastAPI アプリ本体を作成
app = FastAPI(title="勤怠管理システム", debug=settings.debug)

# ---------------------------------------------------------------------------
# セッション管理（署名付きクッキー方式）
#   secret_key : Cookie の署名に使う秘密鍵（.env の SECRET_KEY）
#   same_site  : lax（同一サイトのみ送信を基本とする。CSRF 対策の一助）
#   https_only : True にすると Secure 属性（HTTPS のみ送信）。開発時は False
#   注: HttpOnly 属性は自動で付与される（JavaScript から Cookie を読めない）
# ---------------------------------------------------------------------------
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.secret_key,
    session_cookie="session",
    max_age=14 * 24 * 60 * 60,  # 14 日間有効（秒）
    same_site="lax",
    https_only=False,  # 本番（HTTPS）運用時は True にする
)

# ---------------------------------------------------------------------------
# ルーターの登録
# ---------------------------------------------------------------------------
app.include_router(auth.router)
app.include_router(home.router)


# ---------------------------------------------------------------------------
# エラーハンドラ
# ---------------------------------------------------------------------------
@app.exception_handler(403)
async def forbidden_handler(request: Request, exc):
    """権限エラー（403）を専用画面で表示する。"""
    return templates.TemplateResponse(request, "errors/403.html", status_code=403)


@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    """ページ不存在（404）を専用画面で表示する。"""
    return templates.TemplateResponse(request, "errors/404.html", status_code=404)