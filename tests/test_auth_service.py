# =============================================================================
# サービス層（AuthService）のテスト
# -----------------------------------------------------------------------------
# pytest で自動テストする。実行: .venv/bin/pytest tests/ -v
# fixture で「セッションの用意」と「テストデータの投入・後片付け」を共通化する。
# =============================================================================
from datetime import date, time

import pytest

from app.core.security import hash_password
from app.db.session import SessionLocal
from app.models.department import Department
from app.models.employee import Employee
from app.models.work_schedule import WorkSchedule
from app.services.auth_service import AuthService

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
        password_hash=hash_password("pass123"),   # 本物のハッシュ
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

#ここまではtest_employee_repositoryと同じ
#ここからauth_serviceのテスト

def test_authenticate_success(db, employee):
    """
    正しい社員番号とパスワードでログイン成功
    """
    found = AuthService(db).authenticate("TEST001", "pass123")
    assert found is not None
    assert found.full_name == "テスト 太郎"

def test_authenticate_wrong_password(db, employee):
    """
    間違ったパスワードでログイン失敗
    """
    found = AuthService(db).authenticate("TEST001", "wrong-password")
    assert found is None
    
def test_authenticate_unknown_employee(db):
    """
    存在しない社員番号でログイン失敗
    """
    found = AuthService(db).authenticate("NO_SUCH", "pass123")
    assert found is None   

def test_authenticate_retired(db, employee):
    """
    退職済みの社員でログイン失敗
    """
    employee.retire_date = date(2026, 1, 1)   # 過去の日付 → can_login() が False
    db.commit()
    found = AuthService(db).authenticate("TEST001", "pass123")
    assert found is None

def test_authenticate_inactive(db, employee):
    """
    無効な社員でログイン失敗
    """
    employee.is_active = False
    db.commit()
    found = AuthService(db).authenticate("TEST001", "pass123")
    assert found is None    
