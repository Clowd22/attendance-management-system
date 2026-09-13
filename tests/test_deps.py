# =============================================================================
# 認証ガード（deps）のテスト
# -----------------------------------------------------------------------------
# get_current_user / require_admin を検証する。
# Request オブジェクトは unittest.mock.MagicMock で偽装する。
# （HTTP リクエスト・セッションに依存するため、単体ではモックが必要）
# =============================================================================
from datetime import date, time
from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException

from app.api.routes.deps import get_current_user, require_admin
from app.db.session import SessionLocal
from app.models.department import Department
from app.models.employee import Employee
from app.models.work_schedule import WorkSchedule


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
        password_hash="dummy-hash",  # deps はパスワード照合をしないので dummy で可
    )
    db.add(emp)
    db.commit()

    yield emp

    db.delete(emp)
    db.commit()
    db.delete(dept)
    db.delete(sched)
    db.commit()


def _make_request(user_id):
    """セッションに user_id を持つ Request の偽物を作る。"""
    request = MagicMock()
    request.session.get.return_value = user_id
    return request


def test_get_current_user_success(db, employee):
    """セッションに有効な user_id があれば、社員が返る。"""
    request = _make_request(employee.id)
    result = get_current_user(request, db)
    assert result is not None
    assert result.id == employee.id


def test_get_current_user_not_logged_in(db):
    """セッションに user_id が無ければ、ログイン画面へリダイレクト。"""
    request = _make_request(None)
    with pytest.raises(HTTPException):
        get_current_user(request, db)


def test_get_current_user_unknown_employee(db):
    """存在しない user_id なら、セッションをクリアしてリダイレクト。"""
    request = _make_request(999999)
    with pytest.raises(HTTPException):
        get_current_user(request, db)
    request.session.clear.assert_called_once()


def test_get_current_user_retired(db, employee):
    """退職済み社員なら、リダイレクト。"""
    employee.retire_date = date(2026, 1, 1)
    db.commit()
    request = _make_request(employee.id)
    with pytest.raises(HTTPException):
        get_current_user(request, db)


def test_require_admin_success(db, employee):
    """管理者なら、社員が返る。"""
    employee.role = Employee.ROLE_ADMIN
    db.commit()
    result = require_admin(employee)
    assert result.id == employee.id


def test_require_admin_forbidden(db, employee):
    """一般社員なら、403 を返す。"""
    with pytest.raises(HTTPException) as exc_info:
        require_admin(employee)
    assert exc_info.value.status_code == 403
