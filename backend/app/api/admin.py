"""Public admin endpoints for bootstrap (master data import without prior login)."""
from flask import Blueprint, current_app, jsonify, request
from flask_jwt_extended import verify_jwt_in_request
from flask_jwt_extended.exceptions import JWTExtendedException

from app.extensions import db
from app.models import User
from app.services.import_xlsx import import_master_data_xlsx
from app.utils.auth import current_user

bp = Blueprint("admin", __name__)


def _admin_token_ok() -> bool:
    expected = (current_app.config.get("ADMIN_IMPORT_TOKEN") or "").strip()
    if not expected:
        return True
    got = (request.headers.get("X-Admin-Token") or request.form.get("admin_token") or "").strip()
    return got == expected


def _has_users() -> bool:
    return db.session.query(User.id).first() is not None


@bp.get("/status")
def admin_status():
    """Whether DB has users (for UI hints)."""
    return jsonify(
        {
            "has_users": _has_users(),
            "admin_token_required": bool(
                (current_app.config.get("ADMIN_IMPORT_TOKEN") or "").strip()
            ),
        }
    )


@bp.post("/master-data/import")
def admin_import_master_data():
    """
    Import XLSX (clears documents and master data).

    - If ADMIN_IMPORT_TOKEN is set: only the token (header or form) is required.
    - If it is not set and the DB has no users: anonymous bootstrap import is allowed.
    - If it is not set and users already exist: a valid JWT is required.
    """
    if not _admin_token_ok():
        return jsonify({"error": "Invalid or missing admin token"}), 403

    expected = (current_app.config.get("ADMIN_IMPORT_TOKEN") or "").strip()
    if not expected and _has_users():
        try:
            verify_jwt_in_request(optional=False)
        except JWTExtendedException:
            return jsonify(
                {
                    "error": "Login required: import would wipe existing data. "
                    "Sign in or set ADMIN_IMPORT_TOKEN and pass X-Admin-Token."
                }
            ), 401
        if not current_user():
            return jsonify({"error": "Unauthorized"}), 401

    if "file" not in request.files:
        return jsonify({"error": "file required"}), 400
    f = request.files["file"]
    raw = f.read()
    if not raw:
        return jsonify({"error": "empty file"}), 400
    try:
        stats = import_master_data_xlsx(raw)
    except Exception as exc:  # noqa: BLE001
        return jsonify({"error": str(exc)}), 400

    logins = [
        row[0]
        for row in db.session.query(User.login_name)
        .order_by(User.login_name)
        .limit(15)
        .all()
    ]
    stats["sample_login_names"] = logins
    return jsonify(stats), 200
