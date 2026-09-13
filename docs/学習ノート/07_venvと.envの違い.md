# config.py の理解確認と、venv と .env の違い

| 項目 | 内容 |
|------|------|
| 作成日 | 2026-09-13 |
| 種別 | 概念理解（設定・実行環境） |

## 質問

> config.pyについて。BaseSettingsってのはpydantic_settingsの中のプロパティ？でいいですかね。で、これでまずこのプロジェクトで使用する設定を決めていると。ここでのdatabase_url:strもDBの接続先ですよね。これをひとまとめにしてsettingクラスのオブジェクトを返すメソッドがget_settingですか？ここで、まだ疑問なのがいまだにvenvとか.envがやっぱりわかってないわ。

## 回答の要旨（結論）

理解は**ほぼ合っている**。ただし `BaseSettings` は「プロパティ」ではなく「**クラス（親クラス）**」、`get_settings` は「メソッド」ではなく「**関数**」が正確。

核心の疑問「venv と .env」は、**名前（先頭のドット）が似ているだけで全く別物**。venv は「実行環境（Python＋ライブラリ）の箱」、.env は「設定値のファイル」。

## 理解チェック

| 理解 | 判定 | 補足 |
|------|------|------|
| `BaseSettings` は pydantic_settings のプロパティ？ | ❌ クラス | `pydantic_settings` ライブラリが提供する親クラス。継承すると .env 読み込み機能が付く |
| これでこのプロジェクトの設定を決めている | ✅ 正解 | `Settings` に `app_env` / `debug` / `secret_key` / `database_url` を定義 |
| `database_url: str` は DB の接続先 | ✅ 正解 | SQLite なら「ファイルの場所」 |
| まとめてオブジェクトを返すのが `get_settings` | ✅ ほぼ正解 | `Settings()` を作って返す**関数**。`@lru_cache` で1回だけ作成 |

## config.py の構造（図）

```
pydantic_settings（ライブラリ）
  └─ BaseSettings（親クラス） … .env を読む機能を持つ
        ▲ 継承
  class Settings(BaseSettings):
      app_env: str = "dev"           … .env の APP_ENV に対応
      debug: bool = True             … DEBUG に対応
      secret_key: str = "..."        … SECRET_KEY に対応
      database_url: str = "..."      … DATABASE_URL に対応
        ▲ 生成して返す
  def get_settings() -> Settings:    … return Settings()
      （@lru_cache で 1回だけ生成）
```

- `.env` の「大文字の変数名」が「小文字のプロパティ名」に対応（`APP_ENV` → `app_env`）。
- `get_settings()` は `Settings()` を生成して返すだけの関数。キャッシュで読み直しを防ぐ。

## venv と .env の違い

```
.venv/（フォルダ）                .env（ファイル）
 └ 仮想環境                       └ 設定値のメモ
    Python + ライブラリの箱          APP_ENV=dev などの「キー=値」
```

| | `.venv`（仮想環境） | `.env`（環境変数ファイル） |
|---|---|---|
| 正体 | フォルダ | ファイル |
| 中身 | Python 本体 + fastapi などのライブラリ | `APP_ENV=dev` などの設定値 |
| 役割 | 実行環境の隔離（他プロジェクトと混ぜない） | 設定の保存（起動時に読む） |
| 誰が使う | コマンド実行時（`.venv/bin/python`） | `config.py` が読み込む |

### venv（仮想環境）とは

「このプロジェクト専用の Python とライブラリの箱」。

```bash
.venv/bin/python                # このプロジェクト専用の Python
.venv/bin/pip install fastapi   # この箱の中にだけライブラリを入れる
```

システム全体の Python に直接入れると別プロジェクトとバージョン衝突するため、プロジェクトごとに箱を作って隔離する。

### .env（環境変数ファイル）とは

「アプリの設定値を書いたメモ」。

```bash
# .env の中身（例）
APP_ENV=dev
DEBUG=true
SECRET_KEY=xxxxxxxx
DATABASE_URL=sqlite:///./data/attendance.db
```

`Settings`（`BaseSettings`）がこれを読んで各プロパティに値を入れる。秘密情報を含むため `.gitignore` で除外される。

## 例え

| 項目 | 例え |
|------|------|
| `.venv` | 「プロジェクト専用の工具箱」。システムの工具箱を共有すると道具がごちゃ混ぜになるので専用の箱を用意 |
| `.env` | 「設定の付箋」。起動時に読む「ここは dev モード、DB はここ」というメモ |

## 補足：そもそも「環境変数」とは

- 環境変数 = OS やプロセスが持つ「名前 = 値」のペア（例：`PATH`、`HOME`）。
- 本来はコマンドで設定するが、多いと面倒なので `.env` に書き出し、pydantic-settings が「あたかも環境変数のように」読み込む。

## 環境変数はどこで確認できるか

### 1. OS（シェル）の環境変数

ターミナルで以下を実行して確認する。

```bash
env          # 全部の環境変数を一覧表示
printenv     # 同じく全部表示
printenv HOME   # 特定の1つだけ表示
echo $HOME      # 同じ（$付きで参照）
```

| 変数 | 意味 | 表示例 |
|------|------|--------|
| `HOME` | ホームディレクトリ | `/Users/apple` |
| `SHELL` | 使っているシェル | `/bin/zsh` |
| `PATH` | コマンドを探す場所の一覧 | `/usr/local/bin:...` |
| `PWD` | 今いるディレクトリ | `/Users/apple/python_lesson/...` |

### 2. プロジェクトの `.env` ファイル（別物）

```bash
cat .env   # プロジェクトルートで実行
```

OS の環境変数ではなく、pydantic-settings が「環境変数だと思って読む」ためのファイル。`SECRET_KEY` など秘密情報を含むので、GitHub や会話に貼らない。

### 2つの「環境変数」の見分け方

| | OS の環境変数 | `.env` ファイル |
|---|---|---|
| 確認方法 | `env` / `printenv` | `cat .env` |
| 誰が設定 | OS・シェル | 自分で手書き |
| 用途 | システム全体 | このアプリの設定 |
| 読み手 | シェル・プログラム全般 | `config.py` の `BaseSettings` |

「環境変数」には2つの顔があり、普段 `env` で見るのは「OS の環境変数」、このプロジェクトで話題なのは「`.env` ファイルに書いたアプリ用の設定」。config.py が読むのは後者。

## env 出力の読み方（実例）

`env` を実行すると「名前=値」の並びが表示される。代表的なもの：

| 変数 | 値 | 意味 |
|------|-----|------|
| `SHELL` | `/bin/zsh` | 使っているシェル |
| `HOME` | `/Users/apple` | ホームディレクトリ |
| `USER` / `LOGNAME` | `apple` | ログインユーザー名 |
| `LANG` | `ja_JP.UTF-8` | 言語・文字コード |
| `PWD` | （プロジェクトパス） | 今いる場所 |
| `VIRTUAL_ENV` | （プロジェクトパス）`/.venv` | 今使っている仮想環境の場所 |
| `PATH` | （先頭に `.venv/bin`） | コマンドを探す場所の一覧 |

### 「venv をアクティブにする」＝環境変数を書き換えるだけ

```
アクティブにする前
  PATH = /usr/local/bin:/usr/bin:...        ← システムの python が使われる

アクティブにした後
  VIRTUAL_ENV = /.../プロジェクト/.venv      ← 印を立てる
  PATH = /.../.venv/bin:/usr/local/bin:...   ← 先頭に .venv/bin を追加

→ `python` と打つだけで .venv/bin/python が優先して呼ばれる
```

つまり `.venv/bin/python` とフルパスで書くのは「確実に仮想環境の Python を呼ぶ」安全策で、アクティブなら `python` だけでも同じ。

### 注意

`env` の出力には認証情報（トークン・API キー関連）も混ざる。自分で確認するのは OK だが、外部に貼ったりスクリーンショットを共有しないこと。

## 関連ファイル・次のステップ

- `app/core/config.py`（`Settings`・`get_settings`）
- `.env`（設定値。git 管理外）
- `.venv/`（仮想環境。git 管理外）
- `docs/03_詳細設計書.md` ステップ1（設定モジュール）
