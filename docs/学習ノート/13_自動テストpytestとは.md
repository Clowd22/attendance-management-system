# 自動テスト（pytest）とは

| 項目 | 内容 |
|------|------|
| 作成日 | 2026-09-13 |
| 種別 | 概念理解（自動テスト） |

## 質問

> こういう検証って実際にはうまくいかないことも多いとは思いますが、毎回こんなコードを書いていたらキリがないというかそのコードが合っているのかまた検証しないといけないわけで。もっと簡単な方法ありませんか。

## 回答の要旨（結論）

「**pytest による自動テスト**」が答え。テストコードに `assert`（期待値の宣言）を書き、`pytest` コマンド一発で自動判定する。一度書けば何度でも再実行でき、コードの変更で壊れたら自動で検出してくれる。

## 手動検証の問題点

- 毎回コピペでスクリプトを書く → キリがない
- 結果を目で見て判定する → 見落とす
- スクリプトは実行したら消える → 資産として残らない

## pytest の仕組み

1. テストコードに `assert`（「〜であるべき」という宣言）を書く
2. `pytest` コマンド一発で全テストを実行し、自動判定
3. 結果は「PASSED / FAILED」で表示（目視確認しない）

## 具体例：リポジトリのテスト

```python
# tests/test_employee_repository.py
def test_get_by_employee_number(db, employee):
    repo = EmployeeRepository(db)
    found = repo.get_by_employee_number("TEST001")
    assert found is not None              # 「見つかるべき」
    assert found.full_name == "テスト 太郎"  # 「名前はこれであるべき」

def test_not_found(db):
    repo = EmployeeRepository(db)
    assert repo.get_by_employee_number("NO_SUCH") is None  # 「None であるべき」
```

## fixture で「準備・後片付け」も共通化

`@pytest.fixture` を使うと、「部署・勤務体系を作る」「後片付けする」部分を一度書くだけで、各テストは「社員が既に用意されている」前提で書ける。

## 「テストコード自体が合ってるか」問題への回答

100% は解決できないが、手動検証とは決定的に違う。

| | 手動スクリプト | pytest 自動テスト |
|---|---|---|
| 再実行 | コピペし直し | `pytest` 一発 |
| 判定 | 目視 | 自動（PASSED/FAILED） |
| 資産性 | 消える | コードとして残る |
| 将来の変更 | 気づかない | 壊れたら FAILED で検出 |

テストコードは「期待値を `assert` で明示」するので何を検証しているか分かり、「1テスト＝1つのこと」でシンプルに保つと間違いも減らせる。自動テストは「将来の自分のための安全網」。

## このプロジェクトでの導入（実行済み）

`requirements.txt` に pytest を追加し、`tests/test_employee_repository.py` を作成した。

### 導入したファイル

| ファイル | 役割 |
|----------|------|
| `requirements.txt` | `pytest>=8.0` を追加 |
| `conftest.py`（ルート） | pytest がルートを `sys.path` に追加するためのファイル |
| `tests/test_employee_repository.py` | リポジトリ層のテスト（3件） |

### 実行方法

```bash
.venv/bin/pytest tests/ -v
```

### 実行結果

```
3 passed in 0.25s
```

### つまずき：`ModuleNotFoundError: No module named 'app'`

最初、pytest 実行時に `app` が見つからずエラーになった。pytest はデフォルトで `tests/` 基準に `sys.path` を設定するため、プロジェクトルートが import パスに含まれない。

→ ルートに `conftest.py` を置くことで解決（pytest は `conftest.py` のあるディレクトリを `sys.path` に追加する）。

### sys.path とは（import の仕組み）

`sys.path` とは「Python が `import` するときに探しに行くフォルダの一覧」。

```
プロジェクトルート
├── app/                    ← app パッケージはここ（ルート直下）
│   └── db/session.py
├── tests/
│   └── test_xxx.py         ← ここで from app.db.session import ...
└── conftest.py             ← ★ これを置くと解決

普通に python で実行するとき：
  sys.path = [カレントディレクトリ(=ルート), ...]
  → ルートが含まれるので app/ が見つかる

pytest で実行するとき：
  sys.path = [tests/, ...]   ← tests/ は入るが「ルート」が入らない
  → app/ が見つからない → ModuleNotFoundError

conftest.py をルートに置くと：
  sys.path = [ルート, tests/, ...]   ← ルートが追加される
  → app/ が見つかる
```

「Python は import するとき `sys.path` に載っているフォルダしか見ない。pytest は `tests/` を入れるが `app/` の親であるルートを入れない」ということ。`conftest.py` を置くと pytest がルートも `sys.path` に追加してくれる。

## 関連ファイル・次のステップ

- `requirements.txt`（pytest 追加）
- `conftest.py`（import パスの解決）
- `tests/test_employee_repository.py`（リポジトリ層のテスト）
- 次のステップ：ステップ8（サービス層）の実装とテスト
