# =============================================================================
# 社員のデータアクセス（リポジトリ）
# -----------------------------------------------------------------------------
# 「DB からどう取り出すか」を担当する。ビジネスルール（ログイン判定など）は
# ここには書かず、サービス層に置く。
# =============================================================================
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.employee import Employee


class EmployeeRepository:
    """社員テーブルに対する読み書きをまとめたクラス。"""

    def __init__(self, db: Session):
        self.db = db

    def get_by_employee_number(self, employee_number: str) -> Employee | None:
        """社員番号で社員を 1 件検索する。見つからなければ None。"""
        stmt = select(Employee).where(Employee.employee_number == employee_number)
        return self.db.execute(stmt).scalar_one_or_none()

    def get_by_id(self, employee_id: int) -> Employee | None:
        """主キー（id）で社員を 1 件取得する。見つからなければ None。"""
        return self.db.get(Employee, employee_id)