# =============================================================================
# ルーター層の統合テスト（TestClient）
# -----------------------------------------------------------------------------
# 実際の HTTP リクエストをシミュレートして、ルーターの挙動を検証する。
# main.py（ステップ12）がまだ無いため、テスト内でアプリを組み立てる。
# TestClient はクッキーを自動で維持するので、ログイン→ホームの流れをテストできる。
# =============================================================================
from datetime import date, time

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from starlette.middleware.sessions import SessionMiddleware

from app.api.routes import auth, home
from app.core.config import get_settings
from app.core.security import hash_password
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
        password_hash=hash_password("pass123"),
    )
    db.add(emp)
    db.commit()

    yield emp

    db.delete(emp)
    db.commit()
    db.delete(dept)
    db.delete(sched)
    db.commit()


@pytest.fixture
def client():
    """テスト用アプリ（SessionMiddleware 込み）の TestClient。"""
    app = FastAPI()
    app.add_middleware(SessionMiddleware, secret_key=get_settings().secret_key)
    app.include_router(auth.router)
    app.include_router(home.router)
    return TestClient(app)


def _login(client, number="TEST001", password="pass123"):
    """ログイン処理を実行するヘルパー。"""
    return client.post(
        "/login",
        data={"employee_number": number, "password": password},
        follow_redirects=False,
    )


# --- ログイン画面・ログイン処理 ---

def test_login_form(client):
    resp = client.get("/login")
    assert resp.status_code == 200
    assert "ログイン" in resp.text


def test_login_empty_fields(client):
    resp = client.post("/login", data={}, follow_redirects=False)
    assert resp.status_code == 400
    assert "社員IDとパスワードを入力してください" in resp.text


def test_login_wrong_password(client, employee):
    resp = _login(client, password="wrong")
    assert resp.status_code == 401
    assert "社員IDまたはパスワードが正しくありません" in resp.text


def test_login_success(client, employee):
    resp = _login(client)
    assert resp.status_code == 303
    assert resp.headers["location"] == "/"


# --- ホーム画面（ログインガード） ---

def test_home_requires_login(client):
    resp = client.get("/", follow_redirects=False)
    assert resp.status_code == 303
    assert resp.headers["location"] == "/login"


def test_home_after_login(client, employee):
    _login(client)
    resp = client.get("/")
    assert resp.status_code == 200
    assert "テスト 太郎" in resp.text


# --- ログアウト ---

def test_logout(client, employee):
    _login(client)
    resp = client.get("/logout", follow_redirects=False)
    assert resp.status_code == 303
    assert resp.headers["location"] == "/login"
