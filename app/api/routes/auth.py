# =============================================================================
# 認証ルーター（ログイン・ログアウト）
# =============================================================================
from fastapi import APIRouter, Depends, Request
from pydantic import ValidationError
from sqlalchemy.orm import Session
from starlette.responses import RedirectResponse

from app.core.templates import templates
from app.db.session import get_db
from app.models.employee import Employee
from app.schemas.auth import LoginForm
from app.services.auth_service import AuthService

# /login などの URL をこのルーターが担当する
router = APIRouter()


@router.get("/login")
async def login_form(request: Request):
    """ログイン画面を表示する。"""
    # すでにログイン済みならホームへ飛ばす（二重ログイン防止）
    if request.session.get("user_id"):
        return RedirectResponse(url="/", status_code=303)

    return templates.TemplateResponse(request, "login.html", {"error": None})


@router.post("/login")
async def login(request: Request, db: Session = Depends(get_db)):
    """ログイン処理。フォームの内容を検証して認証する。"""
    # 1. フォーム（HTML の入力値）を受け取る
    form = await request.form()

    # 2. Pydantic スキーマで入力の形式を検証（空欄など）
    try:
        login_data = LoginForm(
            employee_number=form.get("employee_number", ""),
            password=form.get("password", ""),
        )
    except ValidationError:
        return templates.TemplateResponse(
            request,
            "login.html",
            {"error": "社員IDとパスワードを入力してください"},
            status_code=400,
        )

    # 3. サービス層で認証（存在・有効・パスワード照合）
    auth_service = AuthService(db)
    employee = auth_service.authenticate(
        login_data.employee_number, login_data.password
    )

    # 4. 認証失敗 → 同じ画面にエラーメッセージを表示
    if employee is None:
        return templates.TemplateResponse(
            request,
            "login.html",
            {"error": "社員IDまたはパスワードが正しくありません"},
            status_code=401,
        )

    # 5. 認証成功 → セッションに社員IDを保存してホームへ
    request.session["user_id"] = employee.id
    return RedirectResponse(url="/", status_code=303)


@router.get("/logout")
async def logout(request: Request):
    """ログアウト。セッションを破棄してログイン画面へ戻る。"""
    request.session.clear()
    return RedirectResponse(url="/login", status_code=303)