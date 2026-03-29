from __future__ import annotations

import os

from flask import Flask, flash, redirect, render_template, request, session, url_for
import pandas as pd

from app.config.device_catalog import DEVICE_MODEL_BRANCH_MAP
from app.config.settings import DATASET_PATH
from app.controllers.admin_controller import get_dataset_summary, train_new_model
from app.controllers.auth_controller import validate_login
from app.controllers.user_controller import predict_price


def create_app() -> Flask:
    app = Flask(__name__)
    app.secret_key = os.getenv("APP_SECRET_KEY", "dev-secret-key")

    def _brand_model_map() -> dict[str, list[str]]:
        mapping: dict[str, list[str]] = {}
        for key in DEVICE_MODEL_BRANCH_MAP:
            model, branch = key.split("__", 1)
            mapping.setdefault(branch.title() if branch != "iphone" else "iPhone", []).append(model.title())
        for brand, models in mapping.items():
            models.sort()
        return dict(sorted(mapping.items(), key=lambda item: item[0].lower()))

    def _allowed_brands() -> list[str]:
        return list(_brand_model_map().keys())

    def _normalize_model_branch_key(model_name: str, branch: str) -> str:
        return f"{model_name.strip().lower()}__{branch.strip().lower()}"

    def _parse_int(raw: str, field: str, minimum: int | None = None, maximum: int | None = None) -> int:
        value = int(raw)
        if minimum is not None and value < minimum:
            raise ValueError(f"{field} must be >= {minimum}")
        if maximum is not None and value > maximum:
            raise ValueError(f"{field} must be <= {maximum}")
        return value

    def _parse_float(raw: str, field: str, minimum: float | None = None, maximum: float | None = None) -> float:
        value = float(raw)
        if minimum is not None and value < minimum:
            raise ValueError(f"{field} must be >= {minimum}")
        if maximum is not None and value > maximum:
            raise ValueError(f"{field} must be <= {maximum}")
        return value

    def _build_features_from_form(form: dict) -> tuple[dict, dict]:
        branch = form.get("branch", "").strip()
        model_name = form.get("model", "").strip()
        if not branch:
            raise ValueError("Branch/Brand is required")
        if not model_name:
            raise ValueError("Model is required")

        template = DEVICE_MODEL_BRANCH_MAP.get(_normalize_model_branch_key(model_name, branch), {})
        if not template:
            available = _brand_model_map().get(branch, [])
            if available:
                raise ValueError(f"Model '{model_name}' is not mapped for brand '{branch}'. Available: {', '.join(available)}")
            raise ValueError(f"Brand '{branch}' has no mapped model yet.")

        days_used = _parse_int(form.get("days_used", "365"), "days_used", 1, 5 * 365)

        brand_for_model = template.get("device_brand", branch)
        is_iphone = branch.lower() == "iphone"
        if is_iphone:
            ram = int(template.get("ram", 8))
            storage = _parse_int(form.get("storage", ""), "storage", 8, 1024)
        else:
            ram = _parse_int(form.get("ram", ""), "ram", 1, 32)
            storage = _parse_int(form.get("storage", ""), "storage", 8, 1024)

        battery_health_raw = form.get("battery_health", "").strip().lower()
        battery_health_pct = 80 if battery_health_raw in {"", "unknown", "unk", "u"} else _parse_int(
            battery_health_raw,
            "battery_health",
            1,
            100,
        )
        battery_base = int(template.get("battery_base", 0))
        if battery_base <= 0:
            raise ValueError(f"Model '{model_name}' is missing mapped battery capacity")
        battery_capacity = max(1000, int(round(battery_base * battery_health_pct / 100)))

        screen_size = float(template.get("screen_size", 0))
        camera_mp = float(template.get("back_camera_mp", 0))
        if screen_size <= 0 or camera_mp <= 0:
            raise ValueError(f"Model '{model_name}' is missing mapped screen/camera data")

        normalized_new_price_raw = form.get("normalized_new_price", "").strip()
        normalized_new_price = float(normalized_new_price_raw) if normalized_new_price_raw else template.get("normalized_new_price")

        features = {
            "brand": brand_for_model,
            "ram": ram,
            "storage": storage,
            "battery_capacity": battery_capacity,
            "screen_size": screen_size,
            "camera_mp": camera_mp,
            "branch": branch,
            "model": model_name,
            "days_used": days_used,
            "normalized_new_price": normalized_new_price,
        }
        ui_info = {
            "template_used": bool(template),
            "template": template,
            "battery_health_pct": battery_health_pct,
            "is_iphone": is_iphone,
        }
        return features, ui_info

    def _require_role(*roles: str):
        role = session.get("role")
        if role not in roles:
            return False
        return True

    @app.route("/", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            username = request.form.get("username", "").strip()
            password = request.form.get("password", "")
            role = validate_login(username, password)
            if role is None:
                flash("Invalid username or password", "error")
                return render_template("login.html")
            session["username"] = username
            session["role"] = role
            if role == "data_science":
                return redirect(url_for("data_science"))
            return redirect(url_for("user"))

        if session.get("role") == "data_science":
            return redirect(url_for("data_science"))
        if session.get("role") == "user":
            return redirect(url_for("user"))
        return render_template("login.html")

    @app.route("/logout")
    def logout():
        session.clear()
        return redirect(url_for("login"))

    @app.route("/user", methods=["GET", "POST"])
    def user():
        if not _require_role("user"):
            return redirect(url_for("login"))

        prediction = None
        features = None
        ui_info = None
        form_data: dict[str, str] = {
            "branch": "iPhone",
            "days_used": "365",
        }

        if request.method == "POST":
            form_data = request.form.to_dict(flat=True)
            try:
                features, ui_info = _build_features_from_form(request.form)
                prediction = predict_price(features)
            except Exception as exc:
                flash(str(exc), "error")

        return render_template(
            "dashboard.html",
            role="user",
            username=session.get("username"),
            brand_options=_allowed_brands(),
            model_options_by_brand=_brand_model_map(),
            prediction=prediction,
            features=features,
            ui_info=ui_info,
            form_data=form_data,
            training_metrics=None,
            dataset_stats=None,
        )

    @app.route("/data-science", methods=["GET", "POST"])
    def data_science():
        if not _require_role("data_science"):
            return redirect(url_for("login"))

        prediction = None
        features = None
        ui_info = None
        training_metrics = None
        dataset_stats = None
        form_data: dict[str, str] = {
            "branch": "iPhone",
            "days_used": "365",
        }

        if request.method == "POST":
            action = request.form.get("action", "predict")
            if action == "predict":
                form_data = request.form.to_dict(flat=True)
            try:
                if action == "predict":
                    features, ui_info = _build_features_from_form(request.form)
                    prediction = predict_price(features)
                elif action == "train":
                    records = _parse_int(request.form.get("records", "1000"), "records", 1)
                    distribution = request.form.get("distribution", "uniform")
                    append_only = request.form.get("append_only") == "on"
                    training_metrics = train_new_model(records=records, distribution=distribution, append_only=append_only)
                elif action == "stats":
                    dataset_stats = get_dataset_summary()
            except Exception as exc:
                flash(str(exc), "error")

        return render_template(
            "dashboard.html",
            role="data_science",
            username=session.get("username"),
            brand_options=_allowed_brands(),
            model_options_by_brand=_brand_model_map(),
            prediction=prediction,
            features=features,
            ui_info=ui_info,
            form_data=form_data,
            training_metrics=training_metrics,
            dataset_stats=dataset_stats,
        )

    return app


app = create_app()


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000, debug=True)
