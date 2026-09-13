# C# / SQL Server（SQLClient）と SQLAlchemy の対応

| 項目 | 内容 |
|------|------|
| 作成日 | 2026-09-13 |
| 種別 | 概念理解（他言語・他 DB との対応関係） |

## 質問

> いま私は、SQLServerとC#を会社で勉強していてSQLClientを使ったDB接続およびエンティティクラスの作成でDBを理解しています。今回だとどれがなににあたる？

## 回答の要旨（結論）

C# / SQL Server（SQLClient / ADO.NET）と、今回の Python / SQLAlchemy は **1対1で対応**する。

- ADO.NET の「接続 → コマンド → 実行 → 手動マッピング」が、SQLAlchemy の「engine → session → add/commit → オブジェクト」に対応する。
- 一番の違いは **生 SQL（ADO.NET） vs オブジェクト操作で SQL を自動生成（ORM）** という「レベル」の差。

## 対応表

| 概念 | C# / SQL Server（SQLClient / ADO.NET） | 今回（Python / SQLAlchemy） |
|------|----------------------------------------|------------------------------|
| 接続先の指定 | 接続文字列 `Server=...;Database=...;User Id=...` | `database_url`（`.env` の `sqlite:///...`） |
| DBMS 本体 | SQL Server（サーバー型・ネットワーク越し） | SQLite（ファイル型・ローカル1ファイル） |
| 接続の管理 | `SqlConnection`（`Open()` / `Close()`） | `engine`（`create_engine()`） |
| SQL の実行窓口 | `SqlCommand` + `ExecuteReader()` | `session`（`SessionLocal()`） |
| テーブルの表現 | エンティティクラス（POCO） | models のクラス（`Base` 継承） |
| 結果のマッピング | `reader["id"]` を手動でプロパティに代入 | 自動（ORM がオブジェクトに変換） |
| データ保存 | `INSERT` 文を手書き + `ExecuteNonQuery()` | `session.add(emp)` + `commit()` |
| テーブル作成 | `CREATE TABLE` 手書き ／ EF のマイグレーション | Alembic（`alembic upgrade head`） |

## 各概念の詳細対応

### 1. 接続文字列 ↔ `database_url`

```csharp
// C#：サーバー名・認証が必要
string connStr = "Server=localhost;Database=Attendance;User Id=sa;Password=xxx";
```

```python
# Python：SQLite は「ファイルの場所」だけで済む
database_url = "sqlite:///./data/app.db"
```

どちらも「どこに・どうやって接続するか」を1本の文字列で表す。SQLite は認証・サーバー不要でファイルパスだけ、という違い。

### 2. `SqlConnection` ↔ `engine`

```csharp
using (var conn = new SqlConnection(connStr)) { conn.Open(); ... }
```

```python
engine = create_engine(database_url)
```

どちらも「接続を管理する重いもの」で、アプリ全体で1つあれば十分。

### 3. `SqlCommand` ↔ `session`（一番違う部分）

```csharp
// ADO.NET：SQL を自分で書き、結果を手動マッピング
var cmd = new SqlCommand("SELECT * FROM Employees WHERE id = @id", conn);
using (var reader = cmd.ExecuteReader()) {
    while (reader.Read()) {
        var emp = new Employee { Id = (int)reader["id"], ... };
    }
}
```

```python
# SQLAlchemy：SQL を書かず、オブジェクト操作で自動生成
emp = db.query(Employee).filter(Employee.id == 1).first()
```

`session`（`SessionLocal()`）が `SqlCommand`＋`SqlConnection` の両方の役割を包み込んだ「窓口」。

### 4. エンティティクラス ↔ models のクラス

```csharp
// C# の POCO：ただのデータ入れ物
public class Employee {
    public int Id { get; set; }
    public string LastName { get; set; }
}
```

```python
# SQLAlchemy：クラス自体にテーブル定義が埋め込まれる
class Employee(Base):
    __tablename__ = "employees"
    id: Mapped[int] = mapped_column(primary_key=True)
    last_name: Mapped[str] = mapped_column(String(50))
```

- C# の POCO は「データ入れ物」。テーブルとの対応は別途（EF の属性／ADO.NET の手動マッピング）で指定。
- SQLAlchemy のモデルは「クラス自体にテーブル定義（`__tablename__`・カラム）が埋め込まれる」。

## 例え：接客スタイルの違い

| スタイル | 例え | 実体 |
|----------|------|------|
| ADO.NET（生 SQL） | 自分で注文票（SQL）を書いて厨房に渡す | 全部自分で書く。柔軟だが手間 |
| SQLAlchemy ORM | ウエイターに「社員番号1の人の情報を」と頼むだけ | 裏で SQL を自動生成。便利だが裏が見えにくい |

## 学びの本質

- **ADO.NET（SQLClient）＝ 低レベル**。SQL を自分で書き、結果を自分でエンティティに詰める。
- **SQLAlchemy ORM ＝ 高レベル**。SQL は裏で自動生成、オブジェクト操作だけで完結。

会社で ADO.NET を勉強したおかげで、「ORM が裏で `SELECT` や `INSERT` を生成している」ことが見えやすい。ADO.NET の「接続 → コマンド → 実行 → マッピング」が、SQLAlchemy の「engine → session → add/commit → オブジェクト」と1対1で対応している。

## 関連ファイル・次のステップ

- `app/db/session.py`（`engine`・`SessionLocal`）
- `app/models/`（エンティティクラスに相当）
- `docs/03_詳細設計書.md` ステップ4（Alembic マイグレーション）
- 次のステップ：ステップ4 で DB を初期化（C# でいうテーブル作成に相当）
