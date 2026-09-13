# =============================================================================
# アプリ（main.py）の統合テスト
# -----------------------------------------------------------------------------
# main.py の app をそのまま使って、エラーハンドラ（404）と起動を検証する。
# =============================================================================
import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    return TestClient(app)


def test_not_found(client):
    """存在しない URL は 404 ページを返す。"""
    resp = client.get("/nonexistent")
    assert resp.status_code == 404
    assert "404 - ページが見つかりません" in resp.text


def test_login_form(client):
    """main の app でログイン画面が表示できる。"""
    resp = client.get("/login")
    assert resp.status_code == 200
    assert "ログイン" in resp.text
