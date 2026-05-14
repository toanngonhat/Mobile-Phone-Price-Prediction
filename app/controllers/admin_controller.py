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
    dataset_path: Path = DATASET_PATH,
    n_estimators: int = 100,
    max_depth: int | None = None,
    min_samples_split: int = 2,
    min_samples_leaf: int = 1,
    features: list[str] = None,
) -> dict:
    model = PhonePriceModel()
    if not dataset_path.exists():
        model.build_dataset(dataset_path=dataset_path)
    return model.train_from_dataset(
        dataset_path=dataset_path,
        n_estimators=n_estimators,
        max_depth=max_depth,
        min_samples_split=min_samples_split,
        min_samples_leaf=min_samples_leaf,
        features=features,
    )

def generate_synthetic_records(
    records: int = 1000,
    distribution: str = "uniform",
    append_only: bool = False,
    dataset_path: Path = DATASET_PATH,
) -> dict:
    model = PhonePriceModel()
    model.build_dataset(
        dataset_path=dataset_path,
        synthetic_records=records,
        distribution_profile=distribution,
        append_only=append_only,
    )
    df = pd.read_csv(dataset_path)
    return {"total_rows": len(df), "added_rows": records}


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
                "feature_importances": metadata.get("feature_importances", {}),
                "target": metadata.get("target"),
                "n_estimators": metadata.get("n_estimators", "N/A"),
                "max_depth": metadata.get("max_depth", "N/A"),
                "min_samples_split": metadata.get("min_samples_split", "N/A"),
                "min_samples_leaf": metadata.get("min_samples_leaf", "N/A"),
            }
        )

    return {
        "active_version": active_version,
        "versions": rows,
    }


def get_model_metadata(version: int) -> dict | None:
    version_dir = MODEL_VERSIONS_DIR / f"v{version}"
    metadata_path = version_dir / "metadata.json"
    if metadata_path.exists():
        with open(metadata_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return None


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
        "numeric_distributions": {},
        "usage_price": {},
        "model_performance": {"labels": [], "r2": [], "rmse": [], "mae": []},
        "correlation_heatmap": {"columns": [], "matrix": []},
        "feature_distribution": {},
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

        numeric_vars = ["normalized_used_price", "normalized_new_price", "days_used", "release_year", "screen_size", "battery", "weight", "rear_camera_mp", "front_camera_mp", "internal_memory", "ram"]
        for var in numeric_vars:
            if var in df.columns:
                series = df[var].astype(float).dropna()
                if len(series) > 0:
                    # Compute pre-aggregated boxplot metrics
                    q1 = float(series.quantile(0.25))
                    q3 = float(series.quantile(0.75))
                    median_val = float(series.median())
                    mean_val = float(series.mean())
                    min_val = float(series.min())
                    max_val = float(series.max())

                    # Generate precomputed histogram bins
                    counts, bin_edges = np.histogram(series, bins=40, density=True)
                    bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2

                    payload["numeric_distributions"][var] = {
                        "boxplot": {
                            "q1": round(q1, 2),
                            "median": round(median_val, 2),
                            "q3": round(q3, 2),
                            "min": round(min_val, 2),
                            "max": round(max_val, 2)
                        },
                        "hist": {
                            "x": [round(float(b), 3) for b in bin_centers.tolist()],
                            "y": [round(float(c), 6) for c in counts.tolist()]
                        },
                        "mean": round(mean_val, 2),
                        "median": round(median_val, 2)
                    }
                    try:
                        from scipy.stats import gaussian_kde
                        kde = gaussian_kde(series)
                        x_kde = np.linspace(series.min(), series.max(), 100)
                        y_kde = kde(x_kde)
                        payload["numeric_distributions"][var]["kde_x"] = [round(float(x), 3) for x in x_kde]
                        payload["numeric_distributions"][var]["kde_y"] = [round(float(y), 5) for y in y_kde]
                    except ImportError:
                        pass

        if "normalized_used_price" in df.columns:
            numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
            features = [c for c in numeric_cols if c not in ["id", "model"]]
            sampled = df[features].dropna().sample(
                n=min(250, len(df)),
                random_state=42,
            )
            payload["usage_price"] = {}
            for f in features:
                payload["usage_price"][f] = sampled[f].astype(float).tolist()

        # Calculate Correlation Heatmap for numeric features
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        relevant_cols = [c for c in numeric_cols if c != "id" and c != "model"]
        if relevant_cols:
            corr_matrix = df[relevant_cols].corr(numeric_only=True).round(2).fillna(0)
            payload["correlation_heatmap"]["columns"] = relevant_cols
            payload["correlation_heatmap"]["matrix"] = corr_matrix.values.tolist()

        # Grouped Feature Distributions
        for col, title, suffix in [("device_brand", "Brand", ""), ("os", "OS", ""), ("screen_size", "Screen Size", "inch"), ("rear_camera_mp", "Rear Camera", "MP"), ("front_camera_mp", "Front Camera", "MP"), ("internal_memory", "ROM/Storage", "GB"), ("ram", "RAM", "GB"), ("battery", "Battery", "mAh"), ("weight", "Weight", "g"), ("release_year", "Release Year", "")]:
            if col in df.columns:
                counts = df[col].value_counts().head(7)
                labels = []
                for x in counts.index:
                    try:
                        x_val = f"{int(float(x))} {suffix}" if float(x).is_integer() else f"{x} {suffix}"
                    except:
                        x_val = f"{x} {suffix}"
                    labels.append(x_val.strip())
                payload["feature_distribution"][col] = {
                    "labels": labels,
                    "values": counts.values.tolist(),
                    "title": title
                }

    return payload