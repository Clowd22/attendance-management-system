# =============================================================================
# 認証サービス
# -----------------------------------------------------------------------------
# 「ログインできるか」という業務ルールを担当する。
# DB へのアクセスはリポジトリに任せ、ここでは判定ロジックだけを持つ。
# =============================================================================
from sqlalchemy.orm import Session

from app.core.security import verify_password
from app.models.employee import Employee
from app.repositories.employee_repository import EmployeeRepository


class AuthService:
    """認証（ログイン判定）のサービス。"""

    def __init__(self, db: Session):
        self.db = db
        self.employee_repo = EmployeeRepository(db)

    def authenticate(self, employee_number: str, password: str) -> Employee | None:
        """社員番号とパスワードを検証し、成功したら Employee を返す。

        失敗理由は呼び出し側に教えず、常に None を返す（情報漏えい防止）。
        """
        # 1. 社員番号で社員を探す
        employee = self.employee_repo.get_by_employee_number(employee_number)
        if employee is None:
            return None

        # 2. ログイン可能か（有効・退職していないか）を確認
        if not employee.can_login():
            return None

        # 3. パスワードの照合
        if not verify_password(password, employee.password_hash):
            return None

        # すべてのチェックを通過したら社員を返す
        return employee
