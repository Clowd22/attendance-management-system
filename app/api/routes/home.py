# =============================================================================
# ホームルーター
# =============================================================================
from fastapi import APIRouter, Depends, Request

from app.api.routes.deps import get_current_user
from app.core.templates import templates
from app.models.employee import Employee

router = APIRouter()


@router.get("/")
async def home(
    request: Request,
    current_user: Employee = Depends(get_current_user),  # ← ログイン必須のガード
):
    """ホーム画面。ログイン中社員の情報を表示する。"""
    return templates.TemplateResponse(
        request,
        "home.html",
        {"current_user": current_user},
    )