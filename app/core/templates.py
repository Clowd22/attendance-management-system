# =============================================================================
# Jinja2 テンプレートの設定
# -----------------------------------------------------------------------------
# templates オブジェクトはルーター（auth.py / home.py）で共有する。
# テンプレートのフォルダは app/templates を絶対パスで指定する。
# =============================================================================
import os

from fastapi.templating import Jinja2Templates

# このファイルは app/core/templates.py なので、2つ上の app/ がルートになる
_APP_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# app/templates をテンプレートフォルダに指定する
templates = Jinja2Templates(directory=os.path.join(_APP_DIR, "templates"))