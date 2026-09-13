# =============================================================================
# 勤務体系モデル
# =============================================================================
from datetime import time

from sqlalchemy import Integer, String, Time
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class WorkSchedule(Base):
    """勤務体系マスタ。所定労働時間などの勤務基準を表す。"""

    __tablename__ = "work_schedules"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)  # 体系コード（重複不可）
    name: Mapped[str] = mapped_column(String(100), nullable=False)              # 体系名
    start_time: Mapped[time] = mapped_column(Time, nullable=False)              # 所定始業時刻（例 09:00）
    end_time: Mapped[time] = mapped_column(Time, nullable=False)                # 所定終業時刻（例 18:00）
    required_minutes: Mapped[int] = mapped_column(Integer, nullable=False)      # 所定労働時間（分）
    break_minutes: Mapped[int] = mapped_column(Integer, nullable=False, default=0)  # 休憩時間（分）
    note: Mapped[str | None] = mapped_column(String(255), nullable=True)        # 備考

    # この勤務体系を適用される社員一覧
    employees: Mapped[list["Employee"]] = relationship(back_populates="work_schedule")