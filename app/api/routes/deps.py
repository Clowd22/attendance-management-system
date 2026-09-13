# =============================================================================
# 認証ガード（依存性注入）
# -----------------------------------------------------------------------------
# ルーターの関数の引数に Depends(get_current_user) と書くだけで、
# 「未ログインならログイン画面へ」という制御ができる。
# =============================================================================
from fastapi import Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.employee import Employee


def get_current_user(
    request: Request,
    db: Session = Depends(get_db),
) -> Employee:
    """ログイン中の社員を返す。未ログインならログイン画面へ飛ばす。

    ルーターで `current_user: Employee = Depends(get_current_user)` と
    宣言すると、この関数が自動的に実行される。
    """
    # 1. セッションから user_id を取り出す（ログイン時に保存した値）
    user_id = request.session.get("user_id")
    if user_id is None:
        # 未ログイン → ログイン画面へリダイレクト
        raise HTTPException(status_code=303, headers={"Location": "/login"})

    # 2. user_id で社員を取得
    employee = db.get(Employee, user_id)
    if employee is None or not employee.can_login():
        # 社員が存在しない・無効 → セッションをクリアしてログイン画面へ
        request.session.clear()
        raise HTTPException(status_code=303, headers={"Location": "/login"})

    # 3. ログイン中の社員を返す（画面側で current_user として使う）
    return employee


def require_admin(
    current_user: Employee = Depends(get_current_user),
) -> Employee:
    """管理者専用画面のガード。管理者以外は 403 を返す。

    使い方: `admin: Employee = Depends(require_admin)`
    """
    if not current_user.is_admin():
        raise HTTPException(status_code=403, detail="権限がありません")
    return current_user