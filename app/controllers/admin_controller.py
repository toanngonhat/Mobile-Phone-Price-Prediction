"""Admin controller for dashboard, users, visualizations, and model management."""
from __future__ import annotations

import json
from pathlib import Path
import shutil

import joblib
import numpy as np
import pandas as pd

from app.config.credentials import (
    ADMIN_CREDENTIALS,
    ADMIN_PERMISSION_OPTIONS,
    ADMIN_ROLE,
    DATA_SCIENTIST_CREDENTIALS,
    DATA_SCIENTIST_PERMISSION_OPTIONS,
    DATA_SCIENTIST_ROLE,
)
from app.config.settings import APP_SETTINGS_PATH, DATASET_PATH, MODEL_VERSIONS_DIR
from app.config.settings import RAW_SCHEMA
from app.models.phone_price_model import PhonePriceModel
from app.utils.data_utils import dataset_summary


def train_new_model(
    records: int = 1000,
    distribution: str = "uniform",
    append_only: bool = False,
    dataset_path: Path = DATASET_PATH,
) -> dict:
    model = PhonePriceModel()
    return model.build_dataset_and_train(
        dataset_path=dataset_path,
        synthetic_records=records,
        distribution_profile=distribution,
        append_only=append_only,
    )


def get_dataset_summary(dataset_path: Path = DATASET_PATH) -> dict:
    df = pd.read_csv(dataset_path)
    return dataset_summary(df)


def _normalize_record_frame(raw_df: pd.DataFrame) -> pd.DataFrame:
    df = raw_df.copy()
    required_alt = [c for c in RAW_SCHEMA if c not in {"normalized_used_price", "normalized_new_price"}] + ["used_price", "new_price"]

    has_raw_schema = set(RAW_SCHEMA).issubset(df.columns)
    has_alt_schema = set(required_alt).issubset(df.columns)

    if not has_raw_schema and not has_alt_schema:
        raise ValueError(
            "Record columns invalid. Provide either RAW_SCHEMA columns or RAW_SCHEMA with used_price/new_price."
        )

    if has_alt_schema:
        df["used_price"] = df["used_price"].astype(float)
        df["new_price"] = df["new_price"].astype(float)
        if (df["used_price"] <= 0).any() or (df["new_price"] <= 0).any():
            raise ValueError("used_price and new_price must be positive numbers")
        df["normalized_used_price"] = np.log(df["used_price"])
        df["normalized_new_price"] = np.log(df["new_price"])

    missing = [col for col in RAW_SCHEMA if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    numeric_cast = {
        "screen_size": float,
        "rear_camera_mp": float,
        "front_camera_mp": float,
        "internal_memory": float,
        "ram": float,
        "battery": float,
        "weight": float,
        "release_year": int,
        "days_used": int,
        "normalized_used_price": float,
        "normalized_new_price": float,
    }
    for col, cast_fn in numeric_cast.items():
        df[col] = df[col].astype(cast_fn)

    df["device_brand"] = df["device_brand"].astype(str)
    df["os"] = df["os"].astype(str)

    if (np.exp(df["normalized_used_price"]) <= 0).any() or (np.exp(df["normalized_new_price"]) <= 0).any():
        raise ValueError("normalized prices must map to positive price values")

    return df[RAW_SCHEMA]


def add_manual_record(record_data: dict, dataset_path: Path = DATASET_PATH) -> dict:
    manual_df = pd.DataFrame([record_data])
    normalized_df = _normalize_record_frame(manual_df)

    if dataset_path.exists():
        existing_df = pd.read_csv(dataset_path)
    else:
        existing_df = pd.DataFrame(columns=RAW_SCHEMA)

    merged_df = pd.concat([existing_df[RAW_SCHEMA], normalized_df], ignore_index=True)
    dataset_path.parent.mkdir(parents=True, exist_ok=True)
    merged_df.to_csv(dataset_path, index=False)
    return {
        "added_rows": int(len(normalized_df)),
        "total_rows": int(len(merged_df)),
    }


def import_records_from_csv(file_storage, dataset_path: Path = DATASET_PATH) -> dict:
    if file_storage is None or not getattr(file_storage, "filename", ""):
        raise ValueError("CSV file is required")

    incoming_df = pd.read_csv(file_storage)
    if incoming_df.empty:
        raise ValueError("CSV file is empty")

    normalized_df = _normalize_record_frame(incoming_df)

    if dataset_path.exists():
        existing_df = pd.read_csv(dataset_path)
    else:
        existing_df = pd.DataFrame(columns=RAW_SCHEMA)

    merged_df = pd.concat([existing_df[RAW_SCHEMA], normalized_df], ignore_index=True)
    dataset_path.parent.mkdir(parents=True, exist_ok=True)
    merged_df.to_csv(dataset_path, index=False)
    return {
        "added_rows": int(len(normalized_df)),
        "total_rows": int(len(merged_df)),
        "filename": file_storage.filename,
    }


def _read_settings() -> dict:
    if not APP_SETTINGS_PATH.exists():
        return {}
    with open(APP_SETTINGS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def _write_settings(settings: dict) -> None:
    APP_SETTINGS_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(APP_SETTINGS_PATH, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=2)


def _default_managed_users() -> dict[str, dict]:
    managed_users: dict[str, dict] = {}
    for username, password in ADMIN_CREDENTIALS.items():
        managed_users[username] = {
            "password": password,
            "role": ADMIN_ROLE,
            "permissions": list(ADMIN_PERMISSION_OPTIONS),
        }
    for username, password in DATA_SCIENTIST_CREDENTIALS.items():
        managed_users[username] = {
            "password": password,
            "role": DATA_SCIENTIST_ROLE,
            "permissions": list(DATA_SCIENTIST_PERMISSION_OPTIONS),
        }
    return managed_users


def _default_permissions_for_role(role: str) -> list[str]:
    if role == ADMIN_ROLE:
        return list(ADMIN_PERMISSION_OPTIONS)
    return list(DATA_SCIENTIST_PERMISSION_OPTIONS)


def _normalize_permissions(role: str, permissions: list[str] | None) -> list[str]:
    allowed = set(_default_permissions_for_role(role))
    if permissions is None:
        return sorted(allowed)
    normalized = [str(p) for p in permissions if str(p) in allowed]
    if not normalized:
        return sorted(allowed)
    return sorted(set(normalized))


def _ensure_managed_users() -> dict:
    settings = _read_settings()
    defaults = _default_managed_users()
    managed_users = settings.get("managed_users")
    if isinstance(managed_users, dict) and managed_users:
        dirty = False
        # Only normalize existing accounts here so deletions persist.
        # Default accounts are bootstrapped only when the store is empty.
        for username, profile in managed_users.items():
            role = str(profile.get("role", DATA_SCIENTIST_ROLE)).strip().lower()
            if role not in {ADMIN_ROLE, DATA_SCIENTIST_ROLE}:
                role = DATA_SCIENTIST_ROLE
            normalized_permissions = _normalize_permissions(role, profile.get("permissions"))
            if profile.get("role") != role:
                profile["role"] = role
                dirty = True
            if profile.get("permissions") != normalized_permissions:
                profile["permissions"] = normalized_permissions
                dirty = True
            managed_users[username] = profile
        if dirty:
            settings["managed_users"] = managed_users
            _write_settings(settings)
        return settings

    settings["managed_users"] = defaults
    settings.setdefault("active_model_version", None)
    settings.setdefault("last_training_time", None)
    _write_settings(settings)
    return settings


def list_users() -> list[dict]:
    settings = _ensure_managed_users()
    users = settings.get("managed_users", {})
    default_usernames = set(ADMIN_CREDENTIALS.keys()) | set(DATA_SCIENTIST_CREDENTIALS.keys())

    result: list[dict] = []
    for username, info in sorted(users.items(), key=lambda item: item[0].lower()):
        permissions = info.get("permissions") or []
        if not isinstance(permissions, list):
            permissions = []
        result.append(
            {
                "username": username,
                "role": info.get("role", DATA_SCIENTIST_ROLE),
                "permissions": sorted(set(str(p) for p in permissions)),
                "is_default": username in default_usernames,
            }
        )
    return result


def add_user(username: str, password: str, role: str, permissions: list[str] | None = None) -> None:
    username = username.strip()
    if not username:
        raise ValueError("Username is required")
    if len(password) < 6:
        raise ValueError("Password must have at least 6 characters")

    role = role.strip().lower() if role else DATA_SCIENTIST_ROLE
    if role not in {ADMIN_ROLE, DATA_SCIENTIST_ROLE}:
        raise ValueError("Role must be admin or data_scientist")

    settings = _ensure_managed_users()
    users = settings.get("managed_users", {})
    if username in users:
        raise ValueError(f"User '{username}' already exists")

    users[username] = {
        "password": password,
        "role": role,
        "permissions": _normalize_permissions(role, permissions),
    }
    settings["managed_users"] = users
    _write_settings(settings)


def update_user(
    username: str,
    role: str | None = None,
    password: str | None = None,
    permissions: list[str] | None = None,
) -> None:
    settings = _ensure_managed_users()
    users = settings.get("managed_users", {})
    info = users.get(username)
    if not info:
        raise ValueError(f"User '{username}' not found")

    if role:
        role = role.strip().lower()
        if role not in {ADMIN_ROLE, DATA_SCIENTIST_ROLE}:
            raise ValueError("Role must be admin or data_scientist")
        info["role"] = role

    if password is not None and password.strip() != "":
        if len(password) < 6:
            raise ValueError("Password must have at least 6 characters")
        info["password"] = password

    if permissions is not None:
        info["permissions"] = _normalize_permissions(info.get("role", DATA_SCIENTIST_ROLE), permissions)
    elif role:
        info["permissions"] = _normalize_permissions(info.get("role", DATA_SCIENTIST_ROLE), None)

    users[username] = info
    settings["managed_users"] = users
    _write_settings(settings)


def delete_user(username: str) -> None:
    settings = _ensure_managed_users()
    users = settings.get("managed_users", {})
    if username not in users:
        raise ValueError(f"User '{username}' not found")

    admin_count = sum(1 for item in users.values() if item.get("role") == ADMIN_ROLE)
    if users[username].get("role") == ADMIN_ROLE and admin_count <= 1:
        raise ValueError("Cannot delete the last admin account")

    users.pop(username)
    settings["managed_users"] = users
    _write_settings(settings)


def list_model_versions() -> dict:
    versions: list[int] = []
    if MODEL_VERSIONS_DIR.exists():
        for p in MODEL_VERSIONS_DIR.iterdir():
            if p.is_dir() and p.name.startswith("v"):
                try:
                    versions.append(int(p.name[1:]))
                except ValueError:
                    continue
    versions = sorted(versions)
    settings = _read_settings()
    active_version = settings.get("active_model_version")

    rows: list[dict] = []
    for version in sorted(versions, reverse=True):
        version_dir = MODEL_VERSIONS_DIR / f"v{version}"
        metadata_path = version_dir / "metadata.json"
        metadata = {}
        if metadata_path.exists():
            with open(metadata_path, "r", encoding="utf-8") as f:
                metadata = json.load(f)
        rows.append(
            {
                "version": version,
                "name": f"v{version}",
                "is_active": version == active_version,
                "trained_at": metadata.get("trained_at"),
                "records": metadata.get("records"),
                "r2": metadata.get("r2"),
                "mae": metadata.get("mae"),
                "rmse": metadata.get("rmse"),
                "features": metadata.get("features", []),
                "target": metadata.get("target"),
            }
        )

    return {
        "active_version": active_version,
        "versions": rows,
    }


def set_active_model_version(version: int) -> None:
    model = PhonePriceModel()
    versions = model._available_versions()
    if version not in versions:
        raise ValueError(f"Model version v{version} does not exist")

    settings = _read_settings()
    settings["active_model_version"] = version
    _write_settings(settings)


def delete_model_version(version: int) -> None:
    settings = _read_settings()
    active_version = settings.get("active_model_version")
    if version == active_version:
        raise ValueError("Cannot delete active model version")

    version_dir = MODEL_VERSIONS_DIR / f"v{version}"
    if not version_dir.exists():
        raise ValueError(f"Model version v{version} does not exist")

    shutil.rmtree(version_dir)


def get_admin_visualization_payload(dataset_path: Path = DATASET_PATH) -> dict:
    payload = {
        "overview": {
            "dataset_records": 0,
            "active_model_version": None,
            "total_users": len(list_users()),
            "admin_users": len([u for u in list_users() if u["role"] == ADMIN_ROLE]),
            "data_scientist_users": len([u for u in list_users() if u["role"] == DATA_SCIENTIST_ROLE]),
        },
        "feature_importance": {"labels": [], "values": []},
        "price_distribution": {"bins": [], "counts": []},
        "usage_price": {"x": [], "y": []},
        "model_performance": {"labels": [], "r2": [], "rmse": [], "mae": []},
        "dataset_summary": {},
    }

    model_versions = list_model_versions()
    payload["overview"]["active_model_version"] = model_versions.get("active_version")
    payload["model_performance"]["labels"] = [v["name"] for v in model_versions["versions"][:8]][::-1]
    payload["model_performance"]["r2"] = [v.get("r2") for v in model_versions["versions"][:8]][::-1]
    payload["model_performance"]["rmse"] = [v.get("rmse") for v in model_versions["versions"][:8]][::-1]
    payload["model_performance"]["mae"] = [v.get("mae") for v in model_versions["versions"][:8]][::-1]

    if dataset_path.exists():
        df = pd.read_csv(dataset_path)
        payload["overview"]["dataset_records"] = int(len(df))
        payload["dataset_summary"] = dataset_summary(df)

        if "normalized_used_price" in df.columns:
            prices = np.exp(df["normalized_used_price"].astype(float).dropna())
            if len(prices) > 0:
                counts, bins = np.histogram(prices, bins=12)
                payload["price_distribution"]["bins"] = [round(float(b), 2) for b in bins[:-1]]
                payload["price_distribution"]["counts"] = [int(c) for c in counts]

        if "days_used" in df.columns and "normalized_used_price" in df.columns:
            sampled = df[["days_used", "normalized_used_price"]].dropna().sample(
                n=min(250, len(df)),
                random_state=42,
            )
            payload["usage_price"]["x"] = sampled["days_used"].astype(float).tolist()
            payload["usage_price"]["y"] = np.exp(sampled["normalized_used_price"].astype(float)).round(2).tolist()

    active_version = model_versions.get("active_version")
    if active_version is not None:
        model_path = MODEL_VERSIONS_DIR / f"v{active_version}" / "model.pkl"
        if model_path.exists():
            try:
                pipeline = joblib.load(model_path)
                preprocessor = pipeline.named_steps.get("preprocessor")
                regressor = pipeline.named_steps.get("regressor")
                feature_names = preprocessor.get_feature_names_out().tolist()
                importances = regressor.feature_importances_.tolist()
                pairs = sorted(zip(feature_names, importances), key=lambda item: item[1], reverse=True)[:12]
                payload["feature_importance"]["labels"] = [name.replace("num__", "").replace("cat__", "") for name, _ in pairs]
                payload["feature_importance"]["values"] = [round(float(value), 4) for _, value in pairs]
            except Exception:
                # Keep dashboard responsive even when an old/corrupted model file cannot be deserialized.
                payload["feature_importance"] = {"labels": [], "values": []}

    return payload