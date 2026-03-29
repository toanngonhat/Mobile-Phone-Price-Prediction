"""Authentication controller for login workflows."""

from app.config.credentials import ADMIN_CREDENTIALS, USER_CREDENTIALS


def validate_login(username: str, password: str) -> str | None:
    if ADMIN_CREDENTIALS.get(username) == password:
        return "data_science"
    if USER_CREDENTIALS.get(username) == password:
        return "user"
    return None
