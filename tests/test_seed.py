# =============================================================================
# シードデータ（seed.py）のテスト
# -----------------------------------------------------------------------------
# seed_all() を実行し、期待どおりの件数のデータが投入されるかを検証する。
# 冪等性（何度実行しても同じ初期状態になる）も確認する。
# =============================================================================
from sqlalchemy import func, select

from app.db.session import SessionLocal
from app.models.department import Department
from app.models.employee import Employee
from app.models.leave_type import LeaveType
from app.models.work_schedule import WorkSchedule
from app.seed import seed_all


def _count(model) -> int:
    """指定したモデルの件数を返す。"""
    db = SessionLocal()
    try:
        return db.scalar(select(func.count()).select_from(model))
    finally:
        db.close()


def test_seed_creates_employees():
    seed_all()
    assert _count(Employee) == 6


def test_seed_creates_departments():
    seed_all()
    assert _count(Department) == 3


def test_seed_creates_work_schedules_and_leave_types():
    seed_all()
    assert _count(WorkSchedule) == 1
    assert _count(LeaveType) == 4


def test_seed_has_one_admin():
    seed_all()
    db = SessionLocal()
    try:
        admins = db.scalars(
            select(Employee).where(Employee.role == Employee.ROLE_ADMIN)
        ).all()
        assert len(admins) == 1
    finally:
        db.close()


def test_seed_is_idempotent():
    seed_all()
    seed_all()  # 2回実行しても同じ
    assert _count(Employee) == 6
