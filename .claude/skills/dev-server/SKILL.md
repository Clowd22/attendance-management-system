---
name: dev-server
description: このリポジトリの開発サーバーの起動・DB初期化・動作確認の手順。アプリを実行・確認したいときに使用する。
---

# 開発サーバーの起動と動作確認

このプロジェクト（勤怠管理システム）の開発環境でのサーバー起動・確認手順。

## 前提

- 仮想環境は `./.venv` に作成済みであること（無ければ作成する）

```bash
# 仮想環境が無い場合
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

## 1. 環境変数の準備

`.env` が無ければ `.env.example` からコピーする。

```bash
cp .env.example .env
```

## 2. データベースの初期化

初回起動時やスキーマ変更後はマイグレーションを実行する。

```bash
# マイグレーション未作成の場合
.venv/bin/alembic upgrade head

# マイグレーションスクリプトの生成（モデル変更時）
.venv/bin/alembic revision --autogenerate -m "変更内容の説明"

# シードデータ投入（テスト用ダミーデータ）
.venv/bin/python -m app.seed
```

## 3. 開発サーバーの起動

```bash
# ホットリロード付き（コード変更で自動再起動）で起動
.venv/bin/uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

- アプリ: http://127.0.0.1:8000
- ログイン画面: http://127.0.0.1:8000/login
- APIドキュメント（Swagger UI）: http://127.0.0.1:8000/docs

## 4. 動作確認の手順

1. `/login` にアクセスし、シードデータで作成した社員ID/パスワードでログインできることを確認
2. ホーム画面の打刻ボタンで打刻できることを確認
3. 管理者アカウントで月次集計画面にアクセスできることを確認

## 注意点

- SQLite を使用しているため、同時実行・並列アクセス時の排他制御に注意
- デバッグ時は `.env` の `DEBUG=True` を確認
- サーバー停止は `Ctrl+C`
