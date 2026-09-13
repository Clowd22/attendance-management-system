# =============================================================================
# テンプレート（HTML）のテスト
# -----------------------------------------------------------------------------
# Jinja2 でテンプレートを直接レンダリングし、重要な要素が含まれるかを検証する。
# 「見た目が完全に正しいか」は自動テストでは難しいため、
# 「重要な要素（フォーム・ラベル・表示値）の存在」に絞って確認する。
# =============================================================================
from unittest.mock import MagicMock

import pytest
from jinja2 import Environment, FileSystemLoader


@pytest.fixture
def env():
    """Jinja2 の環境（テンプレートを app/templates/ から読み込む）。"""
    return Environment(loader=FileSystemLoader("app/templates"))


def _make_user(name="テスト 太郎", dept="エンジニア部", is_admin=False):
    """home.html に渡す current_user の偽物を作る。"""
    user = MagicMock()
    user.full_name = name
    user.department.name = dept
    user.is_admin.return_value = is_admin
    return user


# --- login.html ---

def test_login_has_form(env):
    html = env.get_template("login.html").render()
    assert '<form method="post" action="/login">' in html


def test_login_has_inputs(env):
    html = env.get_template("login.html").render()
    assert 'name="employee_number"' in html
    assert 'name="password"' in html


def test_login_shows_error(env):
    html = env.get_template("login.html").render(error="社員番号またはパスワードが違います")
    assert "社員番号またはパスワードが違います" in html


# --- home.html ---

def test_home_shows_name_and_dept(env):
    html = env.get_template("home.html").render(current_user=_make_user())
    assert "テスト 太郎" in html
    assert "エンジニア部" in html


def test_home_shows_employee_role(env):
    html = env.get_template("home.html").render(current_user=_make_user(is_admin=False))
    assert "一般社員" in html


def test_home_shows_admin_role(env):
    html = env.get_template("home.html").render(current_user=_make_user(is_admin=True))
    assert "管理者" in html


# --- base.html ---

def test_base_has_title(env):
    html = env.get_template("base.html").render()
    assert "勤怠管理システム" in html


def test_base_shows_logout_when_logged_in(env):
    html = env.get_template("base.html").render(current_user=_make_user())
    assert 'href="/logout"' in html
