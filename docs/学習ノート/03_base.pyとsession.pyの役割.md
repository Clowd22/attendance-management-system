# base.py と session.py は何をしているのか？

| 項目 | 内容 |
|------|------|
| 作成日 | 2026-09-13 |
| 種別 | 概念理解（DB 接続と ORM の土台） |

## 質問

> db/base.pyとdb/session.pyについて解説してほしい。

## 回答の要旨（結論）

2つのファイルは、SQLAlchemy を使うための**土台（インフラ）**を用意している。

- **`base.py`** ＝ ORM モデル（テーブル定義）側の**共通の親クラス** `Base` を定義する。
- **`session.py`** ＝ DB 接続（エンジン）とセッションの**生成・供給**を担当する。

「モデル側の基盤」と「接続側の管理」という役割分担になっていて、この2つが揃うと初めて「モデルを定義して DB 操作する」という典型的な FastAPI + SQLAlchemy の構成が完成する。

## 全体の関係（図）

```
app/core/config.py  (get_settings: .env から設定を読む)
        │ database_url（接続先の URL）
        ▼
app/db/session.py ──────────────┐
   ├─ engine（接続の親玉）        │ 接続プールを管理
   │    └─ SQLite の PRAGMA 設定  │ 外部キー制約を有効化
   ├─ SessionLocal（セッション工場）
   │    └─ get_db()（Depends 用の取得関数）
   │
app/db/base.py ── Base（モデルの共通親）
        ▲ 継承
   各モデル（Employee など）
        │ 自動で登録される
   Base.metadata ──▶ Alembic マイグレーション
```

## 例え：レストランの厨房とレシピ

| コード上の要素 | 例え | 役割 |
|----------------|------|------|
| `engine` | 厨房の設備（ガス管・換気扇） | DB への接続そのものを管理する。シェフは意識せず、裏で動く |
| `SessionLocal` / セッション | シェフの「まな板・作業台」 | 1つの料理（処理）ごとに使い、終わったら片付ける。複数の皿をまとめて「確定（commit）」できる |
| `Base` | レシピの共通書式 | すべての料理（モデル）が同じ書式で書かれる。書式が集まって「メニュー表（metadata）」になる |
| `get_db()` | ホール係が「必要なときに作業台を1つ出して、終わったら回収」する係 | リクエストごとにセッションを出し入れする |

- **エンジン（厨房設備）** はアプリ全体で1つあればいい「重いもの」。
- **セッション（まな板）** はリクエスト（1品）ごとに都度作って片付ける「軽いもの」。
- この「重いものは1つ、軽いものは都度」という発想が、Web アプリと DB の付き合い方の基本。

## コードの各要素の役割

| コード | 役割 |
|--------|------|
| `class Base(DeclarativeBase)` | 全モデルの親。継承するとテーブル定義が `Base.metadata` に自動登録される |
| `create_engine(settings.database_url, connect_args=...)` | DB への接続を管理するエンジンを作る |
| `check_same_thread=False` | SQLite が「別スレッドからの接続」を拒否する制限を解除（FastAPI はマルチスレッドのため必須） |
| `@event.listens_for(engine, "connect")` | 「接続が確立されるたび」に実行するフック |
| `PRAGMA foreign_keys=ON` | SQLite でデフォルト無効な外部キー制約を有効化（参照整合性を守る） |
| `sessionmaker(autocommit=False, autoflush=False, bind=engine)` | セッションを生成する工場 `SessionLocal` を作る |
| `autocommit=False` | 明示的に `commit()` するまで変更を DB に反映しない |
| `autoflush=False` | 自動 flush（SQL を発行して同期）を止め、タイミングを開発者が制御 |
| `get_db()` の `yield` + `finally` | リクエストごとにセッションを開き、例外が起きても必ず閉じる |

## 補足：なぜこう書くのか

- **SQLite は「1ファイルの DB」で、デフォルトだと外部キー制約が効かない。** そのままだと「存在しない社員IDの打刻」まで保存できてしまう。だから接続のたびに `PRAGMA foreign_keys=ON` を実行して整合性を保つ。
- **`yield` の前後で開閉するのが `get_db()` の本質。** FastAPI の `Depends(get_db)` はこの関数を呼び、`yield db` で受け取った `db` をエンドポイントに渡す。処理が終われば `finally` の `db.close()` が走るので、例外が起きても接続の閉じ忘れ（リーク）が起きない。
- **`startswith("sqlite")` で分岐している**のは、後で DB を PostgreSQL 等に差し替えても「SQLite 専用の対処だけ」を切り分けられるようにするため。設定（`database_url`）を変えるだけで DB を切り替えられる設計。

## 関連ファイル・次のステップ

- `app/db/base.py`（実装：モデルの共通親）
- `app/db/session.py`（実装：エンジン・セッション）
- `app/core/config.py`（設定：`database_url` の供給元）
- `docs/03_詳細設計書.md` ステップ2（DB 基盤）
- 次のステップ：`Base` を継承した最初のモデル（社員など）の定義 → マイグレーション（Alembic）
