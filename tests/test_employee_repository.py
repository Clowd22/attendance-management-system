# =============================================================================
# リポジトリ層（EmployeeRepository）のテスト
# -----------------------------------------------------------------------------
# pytest で自動テストする。実行: .venv/bin/pytest tests/ -v
# fixture で「セッションの用意」と「テストデータの投入・後片付け」を共通化する。
# =============================================================================
from datetime import date, time

import pytest

from app.db.session import SessionLocal
from app.models.department import Department
from app.models.employee import Employee
from app.models.work_schedule import WorkSchedule
from app.repositories.employee_repository import EmployeeRepository


@pytest.fixture
def db():
    """テスト用の DB セッション。テスト後に必ず閉じる。"""
    session = SessionLocal()
    yield session
    session.close()


@pytest.fixture
def employee(db):
    """テスト用の社員（と部署・勤務体系）を用意し、テスト後に後片付けする。"""
    dept = Department(code="TEST", name="テスト部署")
    sched = WorkSchedule(
        code="TEST", name="テスト勤務",
        start_time=time(9, 0), end_time=time(18, 0), required_minutes=480,
    )
    db.add(dept)
    db.add(sched)
    db.commit()

    emp = Employee(
        employee_number="TEST001",
        last_name="テスト", first_name="太郎",
        last_name_kana="テスト", first_name_kana="タロウ",
        department_id=dept.id,
        employment_type="seishain",
        work_schedule_id=sched.id,
        hire_date=date(2026, 1, 1),
        password_hash="dummy-hash",
    )
    db.add(emp)
    db.commit()

    yield emp

    # 後片付け（外部キー制約のため、参照元の社員を先に消す）
    db.delete(emp)
    db.commit()
    db.delete(dept)
    db.delete(sched)
    db.commit()


def test_get_by_employee_number(db, employee):
    """社員番号で検索して、正しい社員が取れること。"""
    repo = EmployeeRepository(db)
    found = repo.get_by_employee_number("TEST001")
    assert found is not None
    assert found.full_name == "テスト 太郎"


def test_get_by_id(db, employee):
    """主キー（id）で検索して、正しい社員が取れること。"""
    repo = EmployeeRepository(db)
    found = repo.get_by_id(employee.id)
    assert found is not None
    assert found.full_name == "テスト 太郎"


def test_get_by_employee_number_not_found(db):
    """存在しない社員番号は None を返すこと。"""
    repo = EmployeeRepository(db)
    assert repo.get_by_employee_number("NO_SUCH") is None
