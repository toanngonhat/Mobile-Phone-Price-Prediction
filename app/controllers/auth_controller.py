from __future__ import annotations
"""Authentication controller for login workflows."""

import json

from app.config.credentials import (
    ADMIN_CREDENTIALS,
    ADMIN_PERMISSION_OPTIONS,
    ADMIN_ROLE,
    DATA_SCIENTIST_CREDENTIALS,
    DATA_SCIENTIST_PERMISSION_OPTIONS,
    DATA_SCIENTIST_ROLE,
)
from app.config.settings import APP_SETTINGS_PATH


def _read_settings() -> dict:
    if not APP_SETTINGS_PATH.exists():
        return {}
    with open(APP_SETTINGS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def _build_default_users() -> dict[str, dict]:
    users: dict[str, dict] = {}
    for username, password in ADMIN_CREDENTIALS.items():
        users[username] = {
            "password": password,
            "role": ADMIN_ROLE,
            "permissions": ADMIN_PERMISSION_OPTIONS,
        }
    for username, password in DATA_SCIENTIST_CREDENTIALS.items():
        users[username] = {
            "password": password,
            "role": DATA_SCIENTIST_ROLE,
            "permissions": DATA_SCIENTIST_PERMISSION_OPTIONS,
        }
    return users


def _load_managed_users() -> dict[str, dict]:
    settings = _read_settings()
    managed = settings.get("managed_users")
    if isinstance(managed, dict) and managed:
        migrated = False
        for username, profile in managed.items():
            role = str(profile.get("role", DATA_SCIENTIST_ROLE)).strip().lower()
            if role not in {ADMIN_ROLE, DATA_SCIENTIST_ROLE}:
                profile["role"] = DATA_SCIENTIST_ROLE
                migrated = True
            managed[username] = profile
        if migrated:
            settings["managed_users"] = managed
            with open(APP_SETTINGS_PATH, "w", encoding="utf-8") as f:
                json.dump(settings, f, indent=2)
        return managed
    return _build_default_users()


def validate_login(username: str, password: str) -> str | None:
    managed_users = _load_managed_users()
    user_info = managed_users.get(username)
    if user_info and user_info.get("password") == password:
        role = str(user_info.get("role", DATA_SCIENTIST_ROLE)).strip().lower()
        return role if role in {ADMIN_ROLE, DATA_SCIENTIST_ROLE} else DATA_SCIENTIST_ROLE
    return None
