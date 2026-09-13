# models と DB の関係（設計図と実体）

| 項目 | 内容 |
|------|------|
| 作成日 | 2026-09-13 |
| 種別 | 概念理解（ORM と DB の対応関係） |

## 質問

> modelsとあとDBについて。

## 回答の要旨（結論）

**models は「設計図」、DB は「実体」**。models（`app/models/`）は「どんなテーブルを作るか」を書いた設計図で、DB（`data/` の SQLite ファイル）はデータを実際に保存する実体。この2つを繋ぐのが Alembic（ステップ4）。現時点（ステップ3 完了）では設計図はできたが、DB ファイル（実体）はまだ存在しない。

## 全体の流れ（図）

```
【Python 側＝設計図】
  models/employee.py
    class Employee(Base)         … テーブル employees の設計
      id / employee_number / …   … カラムの設計
        │
        │ Base を継承 → Base.metadata に自動登録
        ▼
  Base.metadata（設計図の束）＝「こういうテーブルを作る」という情報
        │
        │ ステップ4: Alembic が Base.metadata を読んで CREATE TABLE を発行
        ▼
【DB 側＝実体】
  data/ 配下の SQLite ファイル（.db）
    └─ employees テーブル … 実際にデータを保存する場所
```

## 対応関係（Python ↔ DB）

| Python（models） | DB（SQLite） |
|------------------|--------------|
| クラス `Employee` | テーブル `employees` |
| インスタンス `emp = Employee(...)` | 1行（レコード） |
| カラム属性 `emp.last_name` | 列 `last_name` |
| `Base.metadata` | テーブル一覧（スキーマ）の設計図 |
| `session.add(emp)` → `session.commit()` | `INSERT` 実行 |

## 例え：設計図と実物の家

| コード上の要素 | 例え |
|----------------|------|
| models（`Employee` クラス） | 家の**設計図**（間取り・柱の位置） |
| `Base.metadata` | 設計図の**束**（全部の図面をまとめたファイル） |
| Alembic（ステップ4） | 設計図から**実際に家を建てる工務店** |
| DB ファイル（`data/*.db`） | 建った**実物の家**（実際に人が住む＝データが入る） |

- 設計図（models）だけでは「家」は存在しない。工務店（Alembic）が建てて初めて実物になる。
- 設計図を書き換えたら、建て直し（マイグレーションの再実行）が必要。

## 2つの土台（app/db/）との関係

```
models（何を保存するか＝テーブルの「形」）
   ×
session.py の engine（どこに接続するか＝DB の「場所」）
   ↓
session（窓口）を通して SQL が発行され、DB ファイルに読み書きされる
```

- `base.py` の `Base` ＝ models の共通親（設計図の書式）
- `session.py` の `engine` ＝ DB ファイルへの接続窓口
- `models/` の各クラス ＝ テーブルの形
- この3つが揃って初めて「設計図どおりに DB に保存できる」

## 補足：DB はいつ・どうやって作るか

**ステップ4（Alembic マイグレーション）** で作る。

1. Alembic が `Base.metadata`（設計図）を読む
2. `CREATE TABLE` 文を自動生成
3. `data/` に SQLite ファイルができ、テーブルが実体化する

DB 初期化・動作確認の手順は `dev-server` スキルにまとまっている。

## 関連ファイル・次のステップ

- `app/models/`（設計図＝各モデル）
- `app/db/base.py`（`Base`・`Base.metadata`）
- `app/db/session.py`（`engine`・`SessionLocal`・`get_db`）
- `docs/03_詳細設計書.md` ステップ4（Alembic マイグレーション）
- 次のステップ：ステップ4 で DB を初期化し、テーブルを実体化する
