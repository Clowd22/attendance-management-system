# =============================================================================
# データベース接続（エンジン）とセッション
# -----------------------------------------------------------------------------
# SQLAlchemy の「エンジン」は DB への接続を管理する。
# 「セッション」は 1 つの処理単位（トランザクション）を扱う窓口。
# =============================================================================
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

from app.core.config import get_settings

# .env から設定を取得
settings = get_settings()

# SQLite は別スレッドからの接続を拒否するため、check_same_thread=False を指定する
# （FastAPI は複数スレッドで処理するため、これが無いとエラーになる）
connect_args = {}
if settings.database_url.startswith("sqlite"):
    connect_args["check_same_thread"] = False

# エンジンを作成（接続の窓口となる親玉）
engine = create_engine(settings.database_url, connect_args=connect_args)

# SQLite はデフォルトで外部キー制約が無効になっているため、
# 接続のたびに PRAGMA で有効化する
if settings.database_url.startswith("sqlite"):
    @event.listens_for(engine, "connect")
    def _enable_sqlite_foreign_keys(dbapi_connection, _connection_record):
        """SQLite の外部キー制約を有効化するイベントハンドラ。"""
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


# セッションを生成する工場。リクエストごとに SessionLocal() を呼ぶ
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """FastAPI の依存性注入で使う、DB セッションの取得関数。

    リクエストごとに 1 つのセッションを作り、処理が終わったら必ず閉じる。
    yield の前後で「開く / 閉じる」を確実に実行するのがポイント。
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()