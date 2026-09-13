# Pydantic スキーマとログインフォーム検証（ステップ6）

| 項目 | 内容 |
|------|------|
| 作成日 | 2026-09-13 |
| 種別 | 概念理解 + 動作確認 |

## 質問

> あとステップ６を実行した。これがちゃんと動くのかテストしたい

## 回答の要旨（結論）

`app/schemas/auth.py` の `LoginForm` は、Pydantic の `BaseModel` でフォーム入力を「**形式**」検証する。テストの結果、正常系・異常系（空文字・長すぎ）すべて期待どおりに動作した。

形式検証（ステップ6）と認証判定（ステップ8 サービス層）は役割が分かれている点が重要。

## テスト結果

| テスト | 入力 | 結果 | 判定 |
|--------|------|------|------|
| 正常系 | `A001` / `pass123` | インスタンス生成成功 | ✅ |
| 異常系1 | 空の社員番号 | `ValidationError` | ✅ |
| 異常系2 | 空のパスワード | `ValidationError` | ✅ |
| 異常系3 | 21文字の社員番号 | `ValidationError` | ✅ |

## 検証方法（自分で実行する場合）

以下のコマンドをプロジェクトルートで実行する。4つのケースが順に表示される。

```bash
.venv/bin/python <<'EOF'
from app.schemas.auth import LoginForm
from pydantic import ValidationError

# 正常系
f = LoginForm(employee_number="A001", password="pass123")
print("正常系 OK:", f.employee_number, "/", f.password)

# 異常系1: 空の社員番号
try:
    LoginForm(employee_number="", password="pass123")
    print("異常系1 NG: エラーにならない")
except ValidationError:
    print("異常系1 OK: 空の社員番号は ValidationError になる")

# 異常系2: 空のパスワード
try:
    LoginForm(employee_number="A001", password="")
    print("異常系2 NG: エラーにならない")
except ValidationError:
    print("異常系2 OK: 空のパスワードは ValidationError になる")

# 異常系3: 長すぎる社員番号（21文字）
try:
    LoginForm(employee_number="A" * 21, password="pass123")
    print("異常系3 NG: エラーにならない")
except ValidationError:
    print("異常系3 OK: 21文字の社員番号は ValidationError になる")
EOF
```

期待される出力：

```
正常系 OK: A001 / pass123
異常系1 OK: 空の社員番号は ValidationError になる
異常系2 OK: 空のパスワードは ValidationError になる
異常系3 OK: 21文字の社員番号は ValidationError になる
```

## コードの意味

```python
class LoginForm(BaseModel):
    employee_number: str = Field(min_length=1, max_length=20)
    password: str = Field(min_length=1, max_length=128)
```

- `BaseModel` を継承したクラスが「どんな型で、どんな制約があるか」を定義する。
- `Field(min_length=1)` = 空文字を禁止。
- `Field(max_length=20)` / `max_length=128` = 長さの上限（DB のカラム長と対応）。

## 一番大事なポイント：形式検証と認証判定は別

| 層 | 担当 | 例 |
|----|------|-----|
| ステップ6（スキーマ） | 形式の検証 | 「空欄でないか」「長すぎないか」 |
| ステップ8（サービス層） | 認証の判定 | 「そのID・パスワードは正しいか」 |

「社員番号が空文字か」はここで弾くが、「その社員番号が実在するか・パスワードが合っているか」はサービス層（ステップ8）で判定する。

## C# / SQL Server との対応

| C# / SQL Server | 今回 |
|-----------------|------|
| DataAnnotations（`[Required]`・`[StringLength]`）や FluentValidation | Pydantic の `Field(...)` |

## 関連ファイル・次のステップ

- `app/schemas/auth.py`（実装）
- `docs/03_詳細設計書.md` ステップ6（ログインフォーム定義）
- 次のステップ：ステップ7（リポジトリ層 `app/repositories/employee_repository.py`）
