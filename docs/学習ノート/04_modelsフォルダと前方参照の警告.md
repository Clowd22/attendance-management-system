# models フォルダと前方参照（Could not find name）の警告

| 項目 | 内容 |
|------|------|
| 作成日 | 2026-09-13 |
| 種別 | 概念理解 + エラー解決（型チェッカーの警告） |

## 質問

> 6.9 確認まで作業を進めましたが、`department: Mapped["Department"] = relationship(back_populates="employees")` と `work_schedule: Mapped["WorkSchedule"] = relationship(back_populates="employees")` について `Could not find name 'Department'` や `Could not find name 'WorkSchedule'` が例外として表示されているが、`.venv/bin/python -c "from app.models import Employee, Department, WorkSchedule, LeaveType; print('モデル OK:', len(Employee.__table__.columns), 'カラム')"` → `モデル OK: 18 カラム` 自体は起動する。一応この models のフォルダについて解説してから、このエラーについても説明して。

## 回答の要旨（結論）

`Could not find name 'Department'` は**実行時の例外ではなく、エディタの型チェッカー（Pylance / Pyright 等）の静的解析が出す警告**。実プログラムは正しく動いている（`モデル OK: 18 カラム` が証拠）。原因は、`Employee` と `Department` の相互参照で循環インポートを避けるため、型名を**文字列（前方参照）**で書いているから。SQLAlchemy は実行時にこの文字列を後から解決するので動く。

## models フォルダの役割

`app/models/` は「DB のテーブル＝ Python クラス」を定義する場所。前回の `app/db/base.py` の `Base` を継承して各テーブルを作る。

| ファイル | モデル（クラス） | 役割 |
|---------|----------------|------|
| `__init__.py` | — | 全モデルを一括 import する入り口。これを import するだけで全モデルが `Base.metadata` に登録される |
| `department.py` | `Department` | 部署マスタ |
| `work_schedule.py` | `WorkSchedule` | 勤務体系マスタ |
| `leave_type.py` | `LeaveType` | 休暇種別マスタ |
| `employee.py` | `Employee` | 社員マスタ（＝ログインユーザー） |

### テーブル同士の関連（図）

```
employees（社員）
  ├─ department_id ──────▶ departments（部署）
  └─ work_schedule_id ───▶ work_schedules（勤務体系）

leave_types（休暇種別）＝ 独立（Phase 0 ではまだ他テーブルと繋がらない）
```

### SQLAlchemy 2.0 の記法（employee.py に出てくる要素）

| コード | 役割 |
|--------|------|
| `Mapped[int]` / `mapped_column()` | カラム定義。Python の型ヒントで型を表す |
| `ForeignKey("departments.id")` | 他テーブルへの外部キー（ID で参照） |
| `relationship(back_populates=...)` | 関連先をオブジェクトとしてたどれるようにする（例：`employee.department.name`） |
| `back_populates="employees"` | 双方向の関連で、相手側のプロパティ名を指定 |

## 例え：循環参照と「後で解決する約束」

| コード上の要素 | 例え |
|----------------|------|
| `Mapped["Department"]`（文字列） | 「部署は、あとで名簿を見て特定する」という約束メモ。今この瞬間は部署が誰か知らなくていい |
| 型チェッカーの警告 | 「名簿に部署の欄がないぞ？」と注意する上司。実際はあとで名簿（`Base.metadata`）に載るので問題ない |
| SQLAlchemy の実行時解決 | 全員分の名簿（`Base.metadata`）が揃ってから、約束メモの「Department」を名簿から探して結びつける |

## 警告（Could not find name）の正体

警告が出るのはこの2行（`employee.py` 53〜54行）。

```python
department: Mapped["Department"] = relationship(back_populates="employees")
work_schedule: Mapped["WorkSchedule"] = relationship(back_populates="employees")
```

ポイントは型名が**文字列（引用符で囲んだ文字）**になっていること。

### なぜ文字列で書くのか＝「前方参照（forward reference）」

`Employee` と `Department` は**相互参照**している。

- `Employee` → `Department`（社員の所属部署）
- `Department` → `Employee`（部署に所属する社員一覧）

両方のファイルで相手を `import` し合うと**循環インポート**（A→B→A→…）が起きて読み込みに失敗する恐れがある。そこで「相手のクラス名は**文字列で書いて後から解決する**」＝前方参照を使う。

```
employee.py の記述
  department: Mapped["Department"] = relationship(...)
                         │
  この時点では Department が何か import されていない（未定義）
  型チェッカー: 「"Department" という名前が見つからないぞ」→ 警告
                         ▼
【実行時】SQLAlchemy が Base.metadata に登録済みの全クラスから
          "Department" という名前を探して解決する
                         ▼
        Department クラスに結びつく（だから動く）
```

### まとめ

- **実行時**：SQLAlchemy が文字列を後から解決するので動く → `モデル OK: 18 カラム`
- **型チェッカー**：`employee.py` のスコープ内に `Department` が import されていないので、文字列を型名として解決できず警告する
- `department.py` の `Mapped[list["Employee"]]` も同様に `Employee` を import していないので、同じ警告が出る

## 補足：実行結果「18 カラム」は正しい

設計書の `6.9 確認` には「`# モデル OK: 19 カラム` と出れば OK」と書いてあるが、実際の `Employee` テーブル定義は **18 カラム**が正解。

`relationship()` はカラムではなく「関連」なので数に含まれない。設計書の「19」は誤記（コメントの数字が1つ多い）で、実行結果 18 が正しい。

## 警告を消したい場合（対処）

実害はないのでそのままでも動く。スッキリさせたい場合は **`TYPE_CHECKING`** で「型チェック時だけ import する」のが定石。

```python
# employee.py の先頭に追加
from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.department import Department
    from app.models.work_schedule import WorkSchedule
```

- `TYPE_CHECKING` は**実行時には `False`** になるので、この import は実際には実行されない（循環インポートを避けられる）。
- 型チェッカーは `TYPE_CHECKING` の中身を読んで `Department` を解決できるので、警告が消える。
- `department.py` / `work_schedule.py` 側も同様に `if TYPE_CHECKING: from app.models.employee import Employee` を足せば、`Mapped[list["Employee"]]` の警告も消える。

## 関連ファイル・次のステップ

- `app/models/__init__.py`（モデル一括読み込み）
- `app/models/employee.py` / `department.py` / `work_schedule.py` / `leave_type.py`（各モデル）
- `app/db/base.py`（モデルの共通親 `Base`）
- `docs/03_詳細設計書.md` ステップ3（ORM モデル）
- 次のステップ：ステップ4（Alembic マイグレーション）でテーブルを DB に反映
