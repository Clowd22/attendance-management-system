# =============================================================================
# パスワードのハッシュ化・照合
# -----------------------------------------------------------------------------
# pwdlib というライブラリを使う。
# 注意: PasswordHash.recommended() は Argon2 を返すため、要件どおり bcrypt を
#       明示的に指定する（rounds=12 は pwdlib のデフォルトと同じ）。
# =============================================================================
from pwdlib import PasswordHash
from pwdlib.hashers.bcrypt import BcryptHasher

# bcrypt 方式でハッシュ化するオブジェクト（rounds=12 = 計算コスト）
_password_hash = PasswordHash([BcryptHasher(rounds=12)])


def hash_password(password: str) -> str:
    """パスワードをハッシュ化して文字列で返す。保存時・シード時に使う。"""
    return _password_hash.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """平文パスワードが、保存済みハッシュと一致するか検証する。

    ハッシュ化してから比較するのではなく、bcrypt の内部で検証する。
    （ハッシュにはランダムな salt が含まれるため、単純な文字列比較はできない）
    """
    return _password_hash.verify(plain_password, hashed_password)