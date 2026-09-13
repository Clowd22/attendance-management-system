# import 文と pydantic_settings / lru_cache

| 項目 | 内容 |
|------|------|
| 作成日 | 2026-09-13 |
| 種別 | 概念理解（import とライブラリ） |

## 質問

> 環境変数がOSの機能を使っているというのは理解した。pydantic_settingsとfunctools import lru_cacheってこの辺はなんなんでしょうか。

## 回答の要旨（結論）

どちらも **import 文**。`pydantic_settings` はサードパーティライブラリで「.env を読む」機能を提供し、`functools.lru_cache` は標準ライブラリで「関数の戻り値をキャッシュする」デコレータ。

分担でいうと、「.env を読む」面倒な部分を pydantic-settings が担当し、「1回だけ読めば十分」という効率化を lru_cache が担当している。

## import 文とは

`from functools import lru_cache` は「`functools` の中から `lru_cache` だけを取り出して使えるようにする」宣言。

| 書き方 | 意味 | 使うとき |
|--------|------|----------|
| `from functools import lru_cache` | 特定のものだけ取り出す | `lru_cache` と直接書ける |
| `import functools` | 全部取り込む | `functools.lru_cache` と書く必要がある |

## 標準ライブラリ vs サードパーティ

| | 標準ライブラリ | サードパーティ |
|---|---|---|
| 例 | `functools` | `pydantic_settings` |
| 提供元 | Python に同梱 | 外部の開発者 |
| インストール | 不要 | `pip install` が必要 |
| このプロジェクト | そのまま使える | `.venv` にインストール済み（requirements.txt） |

## pydantic_settings の正体

- `.env` や環境変数を読んで「型変換・必須チェック」する機能を提供するサードパーティライブラリ。
- この行で2つを取り出す：
  - `BaseSettings` = 親クラス。`class Settings(BaseSettings):` で継承すると「.env を自動で読む」機能が付く。
  - `SettingsConfigDict` = 設定オプションの入れ物。`model_config = SettingsConfigDict(env_file=".env", ...)` の形で「どの .env を読むか」を指定。

## functools と lru_cache

- `functools` = Python に最初から入っている標準ライブラリ。
- `lru_cache` = 関数の戻り値をキャッシュするデコレータ。

```python
@lru_cache
def get_settings() -> Settings:
    return Settings()

get_settings()   # 1回目：Settings() を生成して覚える
get_settings()   # 2回目：覚えた結果を返す（再生成しない）
```

- 1回目だけ `Settings()` を実行し、2回目以降はキャッシュしたオブジェクトを返す。
- 「毎回 .env を読み直す無駄」を省き、どこから呼んでも同じ設定オブジェクトが共有される。
- `@` から始まるデコレータは、関数に機能を後付けする飾り。

## まとめ図

```
config.py の import 2行

from functools import lru_cache
      └─ 標準ライブラリ（最初からある）
         └─ デコレータ：関数の戻り値をキャッシュ

from pydantic_settings import BaseSettings, SettingsConfigDict
      └─ サードパーティ（pip で .venv にインストール済み）
         ├─ BaseSettings：親クラス（.env を読む機能）
         └─ SettingsConfigDict：設定オプションの入れ物
```

## 例え：翻訳係と付箋

| 要素 | 例え |
|------|------|
| `pydantic_settings` | 翻訳係。設定メモ（.env）を読んで、Python が使える形に翻訳してくれる |
| `lru_cache` | 付箋。翻訳結果を付箋に書いて貼っておき、2回目からは付箋を読むだけで済ませる |

## 関連ファイル・次のステップ

- `app/core/config.py`（import と `Settings`・`get_settings`）
- `requirements.txt`（pydantic-settings の依存宣言）
- `docs/03_詳細設計書.md` ステップ1（設定モジュール）
