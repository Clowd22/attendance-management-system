# =============================================================================
# 社員モデル（= ログインユーザー）
# =============================================================================
from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Employee(Base):
    """社員マスタ。ログインID（社員番号）とパスワードもこのテーブルで持つ。"""

    __tablename__ = "employees"

    # --- ロールの定数 ---
    ROLE_ADMIN = "admin"        # 管理者（人事・総務）
    ROLE_EMPLOYEE = "employee"  # 一般社員

    # --- 雇用形態の定数（DBにはコードで保存し、画面表示時に日本語へ変換する） ---
    EMPLOYMENT_TYPE_LABELS = {
        "seishain": "正社員",
        "keiyaku": "契約社員",
        "arbeit": "アルバイト",
    }

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    employee_number: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)  # 社員番号（=ログインID）
    last_name: Mapped[str] = mapped_column(String(50), nullable=False)     # 姓
    first_name: Mapped[str] = mapped_column(String(50), nullable=False)    # 名
    last_name_kana: Mapped[str] = mapped_column(String(100), nullable=False)  # 姓フリガナ
    first_name_kana: Mapped[str] = mapped_column(String(100), nullable=False) # 名フリガナ

    department_id: Mapped[int] = mapped_column(ForeignKey("departments.id"), nullable=False)  # 所属部署
    position: Mapped[str | None] = mapped_column(String(100), nullable=True)  # 役職（任意）
    employment_type: Mapped[str] = mapped_column(String(20), nullable=False)  # 雇用形態
    work_schedule_id: Mapped[int] = mapped_column(ForeignKey("work_schedules.id"), nullable=False)  # 勤務体系
    hire_date: Mapped[date] = mapped_column(Date, nullable=False)          # 入社日
    retire_date: Mapped[date | None] = mapped_column(Date, nullable=True)  # 退職日（入るとログイン不可）
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)  # メールアドレス（任意）

    role: Mapped[str] = mapped_column(String(20), nullable=False, default=ROLE_EMPLOYEE)  # ロール
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)  # パスワードハッシュ
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)  # ログイン可フラグ

    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.now)  # 作成日時
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.now, onupdate=datetime.now
    )  # 更新日時

    # 関連オブジェクト（外部キー先のテーブルをオブジェクトとして参照できる）
    department: Mapped["Department"] = relationship(back_populates="employees")
    work_schedule: Mapped["WorkSchedule"] = relationship(back_populates="employees")

    @property
    def full_name(self) -> str:
        """姓 + 名 を連結して返す（例: テスト 太郎）。"""
        return f"{self.last_name} {self.first_name}"

    def is_admin(self) -> bool:
        """管理者かどうかを判定する。"""
        return self.role == self.ROLE_ADMIN

    def can_login(self) -> bool:
        """ログイン可能か判定する（有効かつ退職していない）。"""
        if not self.is_active:
            return False
        if self.retire_date is not None and self.retire_date <= date.today():
            return False
        return True