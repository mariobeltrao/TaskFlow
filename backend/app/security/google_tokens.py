from cryptography.fernet import Fernet, InvalidToken

from app.core.config import get_settings


def _fernet() -> Fernet:
    key = get_settings().google_token_encryption_key
    if not key:
        raise RuntimeError("GOOGLE_TOKEN_ENCRYPTION_KEY não configurada")
    try:
        return Fernet(key.encode("ascii"))
    except (TypeError, ValueError) as exc:
        raise RuntimeError("GOOGLE_TOKEN_ENCRYPTION_KEY inválida") from exc


def encrypt_google_token(token: str) -> str:
    return _fernet().encrypt(token.encode("utf-8")).decode("ascii")


def decrypt_google_token(encrypted_token: str) -> str:
    try:
        return _fernet().decrypt(encrypted_token.encode("ascii")).decode("utf-8")
    except InvalidToken as exc:
        raise RuntimeError("Não foi possível descriptografar o token Google") from exc
