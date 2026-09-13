# TestClient による統合テスト（ルーター層）

| 項目 | 内容 |
|------|------|
| 作成日 | 2026-09-13 |
| 種別 | 概念理解 + 手順 |

## 質問

> できた。テストしたい

## 回答の要旨（結論）

ルーター層のテストは、これまでの**ユニットテスト**（関数を直接呼ぶ）ではなく、FastAPI の **TestClient による統合テスト**（実際の HTTP リクエストをシミュレート）で行う。ステータスコード・レスポンス本文・リダイレクト先を `assert` する。

## ユニットテスト vs 統合テスト

| | ユニットテスト | 統合テスト |
|---|---|---|
| 対象 | 関数・クラス単体 | ルーター（URL と処理の対応） |
| 方法 | 直接呼ぶ | `client.get()` / `client.post()` |
| 検証 | 戻り値 | ステータスコード・本文・リダイレクト |

これまでの repository / service / deps は「関数を直接呼ぶ」ユニットテスト。ルーター層からは「HTTP リクエストを送って検証する」統合テストになる。

## TestClient の使い方

### テスト用アプリの構築

`main.py`（ステップ12）がまだ無いため、テスト内でアプリを組み立てる。**SessionMiddleware の設定が必須**（deps がセッションを使うため）。

```python
app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key=get_settings().secret_key)
app.include_router(auth.router)
app.include_router(home.router)
client = TestClient(app)
```

TestClient は**クッキーを自動で維持**するので、「ログイン → ホーム」の一連の流れをテストできる。

### リダイレクトの検証

```python
resp = client.post("/login", data={...}, follow_redirects=False)
assert resp.status_code == 303
assert resp.headers["location"] == "/"
```

`follow_redirects=False` でリダイレクトを追わず、`303` と `Location` ヘッダーを検証する。

## テストケース設計

| ID | 分類 | 内容 | 期待結果 |
|----|------|------|----------|
| T-RTE-01 | 正常系 | GET /login | 200、ログインフォーム |
| T-RTE-02 | 異常系 | POST /login（空欄） | 400、エラーメッセージ |
| T-RTE-03 | 異常系 | POST /login（誤パスワード） | 401、エラーメッセージ |
| T-RTE-04 | 正常系 | POST /login（正しい） | 303 → `/` |
| T-RTE-05 | 異常系 | GET /（未ログイン） | 303 → `/login` |
| T-RTE-06 | 正常系 | GET /（ログイン済み） | 200、氏名表示 |
| T-RTE-07 | 正常系 | GET /logout | 303 → `/login` |

## つまずき：TestClient に必要な依存パッケージ

最初、テスト収集時にエラーが出た。

1. `httpx2` が無い → `pip install httpx2` で解決（TestClient が依存）
2. `itsdangerous` が無い → `pip install itsdangerous` で解決（SessionMiddleware が依存）

`httpx2` は `requirements.txt` の「開発・テスト」に追記した。

## テスト結果

```
7 passed in 2.32s
```

## 関連ファイル・次のステップ

- `app/api/routes/auth.py` / `home.py`（ルーター）
- `app/core/templates.py`（テンプレート設定）
- `tests/test_routes.py`（統合テスト）
- `docs/03_詳細設計書.md` ステップ11・18章（テスト設計 T-RTE-01〜07）
- 次のステップ：ステップ12（`app/main.py` の実装。実装後は main の app を使った統合テストに置き換え可能）
