from __future__ import annotations

import os

from flask import Flask, flash, redirect, render_template, request, session, url_for

from app.config.credentials import (
    ADMIN_PERMISSION_OPTIONS,
    ADMIN_ROLE,
    DATA_SCIENTIST_PERMISSION_OPTIONS,
    DATA_SCIENTIST_ROLE,
)
from app.config.device_catalog import DEVICE_MODEL_BRANCH_MAP
from app.controllers.admin_controller import (
    add_manual_record,
    add_user,
    delete_model_version,
    delete_user,
    get_admin_visualization_payload,
    get_dataset_summary,
    import_records_from_csv,
    list_model_versions,
    list_users,
    set_active_model_version,
    train_new_model,
    update_user,
)
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

    def _require_role(*roles: str) -> bool:
        role = session.get("role")
        return role in roles

    def _is_management_role() -> bool:
        return _require_role(ADMIN_ROLE, DATA_SCIENTIST_ROLE)

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
            if role in {ADMIN_ROLE, DATA_SCIENTIST_ROLE}:
                return redirect(url_for("admin"))
            return redirect(url_for("user"))

        if session.get("role") in {ADMIN_ROLE, DATA_SCIENTIST_ROLE}:
            return redirect(url_for("admin"))
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
            admin_section="home",
            admin_users=[],
            model_versions={"active_version": None, "versions": []},
            visual_payload={},
            permission_options=ADMIN_PERMISSION_OPTIONS,
        )

    @app.route("/admin", methods=["GET", "POST"])
    def admin():
        if not _is_management_role():
            return redirect(url_for("login"))

        current_role = session.get("role", "")
        can_manage_users = current_role == ADMIN_ROLE

        prediction = None
        features = None
        ui_info = None
        training_metrics = None
        dataset_stats = None
        form_data: dict[str, str] = {
            "branch": "iPhone",
            "days_used": "365",
        }
        manual_record_form: dict[str, str] = {
            "device_brand": "Apple",
            "os": "iOS",
            "screen_size": "6.1",
            "rear_camera_mp": "12",
            "front_camera_mp": "12",
            "internal_memory": "128",
            "ram": "6",
            "battery": "3200",
            "weight": "190",
            "release_year": "2022",
            "days_used": "365",
            "used_price": "650",
            "new_price": "999",
        }
        admin_section = request.args.get("section", "home")
        if admin_section == "users" and not can_manage_users:
            flash("Data scientist role does not have access to user management", "error")
            admin_section = "home"

        if request.method == "POST":
            action = request.form.get("action", "predict")
            section_from_post = request.form.get("section", "")
            if section_from_post:
                admin_section = section_from_post
            if admin_section == "users" and not can_manage_users:
                admin_section = "home"
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
                elif action == "add_user":
                    if not can_manage_users:
                        raise PermissionError("Data scientist role does not have access to user management")
                    permissions = request.form.getlist("permissions")
                    add_user(
                        username=request.form.get("username", ""),
                        password=request.form.get("password", ""),
                        role=request.form.get("role", "user"),
                        permissions=permissions,
                    )
                    flash("User created successfully", "success")
                elif action == "edit_user":
                    if not can_manage_users:
                        raise PermissionError("Data scientist role does not have access to user management")
                    permissions = request.form.getlist("permissions")
                    update_user(
                        username=request.form.get("username", ""),
                        role=request.form.get("role", "user"),
                        password=request.form.get("password") or None,
                        permissions=permissions,
                    )
                    flash("User updated successfully", "success")
                elif action == "delete_user":
                    if not can_manage_users:
                        raise PermissionError("Data scientist role does not have access to user management")
                    target_username = request.form.get("username", "")
                    if target_username == session.get("username"):
                        raise ValueError("You cannot delete the currently logged-in admin")
                    delete_user(username=target_username)
                    flash("User deleted successfully", "success")
                elif action == "set_active_model":
                    version = _parse_int(request.form.get("version", ""), "version", 1)
                    set_active_model_version(version)
                    flash(f"Active model switched to v{version}", "success")
                elif action == "delete_model":
                    version = _parse_int(request.form.get("version", ""), "version", 1)
                    delete_model_version(version)
                    flash(f"Deleted model version v{version}", "success")
                elif action == "add_manual_record":
                    manual_record_form = request.form.to_dict(flat=True)
                    result = add_manual_record(manual_record_form)
                    flash(
                        f"Added {result['added_rows']} record. Dataset now has {result['total_rows']} rows.",
                        "success",
                    )
                elif action == "import_csv_records":
                    csv_file = request.files.get("records_csv")
                    result = import_records_from_csv(csv_file)
                    flash(
                        f"Imported {result['added_rows']} records from {result['filename']}. Dataset now has {result['total_rows']} rows.",
                        "success",
                    )
            except Exception as exc:
                flash(str(exc), "error")

        return render_template(
            "dashboard.html",
            role=current_role,
            username=session.get("username"),
            brand_options=_allowed_brands(),
            model_options_by_brand=_brand_model_map(),
            prediction=prediction,
            features=features,
            ui_info=ui_info,
            form_data=form_data,
            training_metrics=training_metrics,
            dataset_stats=dataset_stats,
            admin_section=admin_section,
            admin_users=list_users(),
            model_versions=list_model_versions(),
            visual_payload=get_admin_visualization_payload(),
            permission_options=ADMIN_PERMISSION_OPTIONS,
            role_permission_options={
                ADMIN_ROLE: ADMIN_PERMISSION_OPTIONS,
                DATA_SCIENTIST_ROLE: DATA_SCIENTIST_PERMISSION_OPTIONS,
                "user": ["predict"],
            },
            can_manage_users=can_manage_users,
            manual_record_form=manual_record_form,
        )

    @app.route("/data-scientist", methods=["GET", "POST"])
    def data_scientist():
        return redirect(url_for("admin"))

    @app.route("/data-science", methods=["GET", "POST"])
    def data_science():
        return redirect(url_for("admin"))

    return app


app = create_app()


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000, debug=True)
