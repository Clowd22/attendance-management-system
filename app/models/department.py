# =============================================================================
# 部署モデル
# =============================================================================
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Department(Base):
    """部署マスタ。社員が所属する部署を表す。"""

    __tablename__ = "departments"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)  # 部署コード（重複不可）
    name: Mapped[str] = mapped_column(String(100), nullable=False)              # 部署名
    note: Mapped[str | None] = mapped_column(String(255), nullable=True)        # 備考

    # この部署に所属する社員一覧（Employee 側の department と相互に参照）
    employees: Mapped[list["Employee"]] = relationship(back_populates="department")