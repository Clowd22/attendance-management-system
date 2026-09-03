# =============================================================================
# アプリケーション設定
# -----------------------------------------------------------------------------
# .env ファイルに書いた環境変数を Python の設定オブジェクトとして読み込む。
# pydantic-settings の BaseSettings を使うと、環境変数の型変換や必須チェックを
# 自動でやってくれる。
# =============================================================================
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """アプリ全体の設定値。

    .env の「大文字の変数名」が「小文字のプロパティ名」に対応する。
    例: APP_ENV  -> app_env
         DEBUG    -> debug
    """

    #: 実行環境（dev / test / prod）
    app_env: str = "dev"

    #: デバッグモード。True のとき詳細なエラーログを出す
    debug: bool = True

    #: セッションの署名に使う秘密鍵（本番では必ず変更する）
    secret_key: str = "change-me-please"

    #: DB 接続文字列
    database_url: str = "sqlite:///./data/attendance.db"

    # SettingsConfigDict で .env ファイルの読み込み方を指定する
    model_config = SettingsConfigDict(
        env_file=".env",          # プロジェクトルートの .env を読む
        env_file_encoding="utf-8",
        extra="ignore",           # 未知の環境変数は無視する
    )


@lru_cache
def get_settings() -> Settings:
    """設定オブジェクトをキャッシュして返す。

    lru_cache を付けることで、何度呼んでも 1 回だけ Settings を作成する。
    （毎回 .env を読み直す無駄を省く）
    """
    return Settings()