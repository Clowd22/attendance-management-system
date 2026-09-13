# HTML テンプレートのテスト

| 項目 | 内容 |
|------|------|
| 作成日 | 2026-09-13 |
| 種別 | 概念理解 + 手順 |

## 質問

> 実装できた。これに関してもテストを実装したいけど、htmlのテストってどうやるんでしょうね。正しく表示されるかどうかなのかな。テストケースから考えて。

## 回答の要旨（結論）

HTML テンプレートのテストは「**重要な要素が含まれているか**」を検証する。「見た目が完全に正しいか」は自動テストでは困難なので、フォームの `action`・入力欄の `name`・表示される値など、重要な要素の存在に絞って `assert` する。

## HTML テストの考え方

- 「見た目の完全な一致」は自動テストでは検証できない
- 現実には「重要な要素（フォーム・ラベル・表示値）の存在」を検証する
- HTML を文字列として見て、期待する要素が含まれるかを `assert`

## テストの2つのレベル

| レベル | 方法 | いつできるか |
|--------|------|-------------|
| 単体（レンダリング） | Jinja2 で直接描画し、文字列を検証 | 今すぐ |
| 統合（TestClient） | エンドポイントにアクセスしてレスポンス HTML を検証 | ルーター実装後 |

現時点ではルーター未実装なので、単体レンダリングテストで「重要な要素の存在」を検証する。見た目の最終確認はブラウザ目視（ステップ14）と TestClient 統合テストで行う。

## テストケース設計

| ID | 分類 | 内容 | 期待結果 |
|----|------|------|----------|
| T-TPL-01 | 正常系 | login.html を描画 | `action="/login"` のフォームがある |
| T-TPL-02 | 正常系 | login.html を描画 | `name="employee_number"` / `name="password"` がある |
| T-TPL-03 | 異常系 | `error` を渡す | エラーメッセージが含まれる |
| T-TPL-04 | 正常系 | home.html に `current_user` を渡す | 氏名が表示される |
| T-TPL-05 | 正常系 | home.html に `current_user` を渡す | 部署名が表示される |
| T-TPL-06 | 正常系 | 管理者を渡す | 「管理者」と表示 |
| T-TPL-07 | 正常系 | 一般社員を渡す | 「一般社員」と表示 |
| T-TPL-08 | 正常系 | base.html を描画 | タイトル「勤怠管理システム」がある |

## 実装のポイント

```python
from jinja2 import Environment, FileSystemLoader

env = Environment(loader=FileSystemLoader("app/templates"))
html = env.get_template("login.html").render()
assert '<form method="post" action="/login">' in html
```

- `current_user` は `full_name`・`department.name`・`is_admin()` を使うので、`MagicMock` で偽装する。
- テンプレート単体では Jinja2 の `Environment` を直接使う（FastAPI の `Jinja2Templates` はルーター実装後に使う）。

## テスト結果

```
8 passed in 0.07s
```

## 関連ファイル・次のステップ

- `app/templates/`（base.html / login.html / home.html / errors/）
- `tests/test_templates.py`（テスト）
- `docs/03_詳細設計書.md` ステップ10・18章（テスト設計 T-TPL-01〜08）
- 次のステップ：ステップ11（ルーター層、TestClient による統合テストが可能になる）
