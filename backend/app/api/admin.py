"""Admin endpoints for master data import (requires manager authentication)."""
from flask import Blueprint, current_app, jsonify, request
from flask_jwt_extended import verify_jwt_in_request
from flask_jwt_extended.exceptions import JWTExtendedException

from app.extensions import db
from app.models import User
from app.services.import_xlsx import import_master_data_xlsx
from app.utils.auth import current_user

bp = Blueprint("admin", __name__)


def _has_users() -> bool:
    return db.session.query(User.id).first() is not None


@bp.get("/status")
def admin_status():
    """Whether DB has users (for UI hints)."""
    return jsonify(
        {
            "has_users": _has_users(),
        }
    )


@bp.post("/master-data/import")
def admin_import_master_data():
    """
    Import XLSX (clears documents and master data).
    Requires a valid JWT token (user must be logged in).
    """
    # Always require valid JWT token
    try:
        verify_jwt_in_request(optional=False)
    except JWTExtendedException:
        return jsonify(
            {
                "error": "Login required: please sign in to import data."
            }
        ), 401
    
    user = current_user()
    if not user:
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
