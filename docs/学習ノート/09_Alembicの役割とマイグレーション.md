# Alembic の役割とマイグレーションのやり方

| 項目 | 内容 |
|------|------|
| 作成日 | 2026-09-13 |
| 種別 | 概念理解（マイグレーションツール） |

## 質問

> ステップ５に行く前にこのステップ４でやりたかったことを教えて。特にテーブルを作りたかったというのはわかりますが、alembicというツールの役割とそのやり方がよくわからない。

## 回答の要旨（結論）

ステップ4でやりたかったことは「**models（設計図）から、実際の SQLite テーブルを作る**」こと。

Alembic は「**DB スキーマの変更をバージョン管理するツール**」で、役割は (1) テーブルの自動生成、(2) スキーマ変更の履歴管理。モデルの設計図を渡せば `CREATE TABLE` を自動で書き、変更履歴を `alembic/versions/` にファイルとして残す。

## Alembic の役割（2つ）

1. **テーブルの自動生成** — models（`Base.metadata`）を読んで `CREATE TABLE` を自動で書く。
2. **スキーマ変更の履歴管理** — 将来「カラム追加」などの変更もバージョンとして記録・適用できる。

`CREATE TABLE` を手書きしてもできないわけではないが、「今 DB がどういう状態か」「いつ何を変えたか」が分からなくなる。Alembic はそれを管理する。

## 例え：Git との対比

Alembic は「**コードの Git**」ならぬ「**DB スキーマの Git**」。

| Git（コード） | Alembic（DBスキーマ） |
|---------------|------------------------|
| コミット | マイグレーションスクリプト（`alembic/versions/*.py`） |
| `HEAD`（今どこにいるか） | `alembic_version` テーブル（どこまで適用済みか） |
| リポジトリ（`.git/`） | `alembic/` フォルダ |
| 変更を記録して共有 | スキーマ変更を記録して再現 |

## ステップ4の5手順、それぞれの意味

| 手順 | コマンド | やっていること |
|------|----------|----------------|
| (1) 初期化 | `alembic init alembic` | 土台（設定・フォルダ）を作る |
| (2) 接続先設定 | `alembic.ini` を編集 | 「どの DB に接続するか」を教える |
| (3) モデル認識 | `env.py` を編集 | 「どの設計図（models）を使うか」を教える |
| (4) スクリプト生成 | `revision --autogenerate` | 設計図と DB を比べて「工事計画書」を作る |
| (5) 適用 | `upgrade head` | 計画書を実行して実際にテーブルを作る |

### ポイント

- (2) と (3) は準備。Alembic に「接続先」と「設計図」を教えるだけ。
- (4) の `--autogenerate` がミソ。models を読んで `CREATE TABLE` を自動で書く。生成された `alembic/versions/*.py` の中身が `CREATE TABLE` の集まり。
- (5) の `upgrade head` で初めて `data/attendance.db` にテーブルが実体化する。

## 例え：家の増改築の工務店

- 設計図（models）と今の家（DB）を比べて、工務店（Alembic）が「必要な工事」を計画書（マイグレーションスクリプト）にまとめる。
- 計画書に承認（`upgrade head`）すると、実際に工事（テーブル作成）が行われる。

## C# / SQL Server との対応

| C# / SQL Server | 今回 |
|-----------------|------|
| EF Core の `Add-Migration` / `Update-Database` | `alembic revision --autogenerate` / `alembic upgrade head` |
| ADO.NET で `CREATE TABLE` を手書き | Alembic が自動生成してくれる |

ADO.NET なら手で書いていた `CREATE TABLE` を、Alembic が設計図から自動で作ってくれる、というのがステップ4の本質。

## 関連ファイル・次のステップ

- `alembic.ini`（接続先設定）
- `alembic/env.py`（モデル認識・`target_metadata = Base.metadata`）
- `alembic/versions/3eb0e3ecf1da_*.py`（生成されたマイグレーションスクリプト）
- `data/attendance.db`（実体化した DB。git 管理外）
- `docs/03_詳細設計書.md` ステップ4（Alembic マイグレーション）
- 次のステップ：ステップ5（パスワード管理 `app/core/security.py`）
