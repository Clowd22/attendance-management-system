# =============================================================================
# 休暇種別モデル
# =============================================================================
from sqlalchemy import Boolean, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class LeaveType(Base):
    """休暇種別マスタ。年次有給休暇・慶弔休暇などの区分を表す。"""

    __tablename__ = "leave_types"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)  # 種別コード（重複不可）
    name: Mapped[str] = mapped_column(String(100), nullable=False)              # 種別名
    grant_days: Mapped[int | None] = mapped_column(Integer, nullable=True)      # 年間付与日数（任意）
    carryover: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)  # 繰越可否
    half_day: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)   # 半日休暇可否
    note: Mapped[str | None] = mapped_column(String(255), nullable=True)        # 備考