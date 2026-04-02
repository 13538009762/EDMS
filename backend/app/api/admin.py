"""Admin endpoints for master data import (requires manager authentication)."""
from flask import Blueprint, current_app, jsonify, request
from flask_jwt_extended import verify_jwt_in_request
from flask_jwt_extended.exceptions import JWTExtendedException

from app.extensions import db
from app.models import User
from app.services.import_xlsx import import_master_data_xlsx
from app.utils.auth import current_user

bp = Blueprint("admin", __name__)


def _has_managers() -> bool:
    return db.session.query(User.id).filter(User.is_manager == True).first() is not None


@bp.get("/status")
def admin_status():
    """Whether DB has managers (for UI hints)."""
    has_users = _has_managers()
    sample_managers = []
    if has_users:
        sample_managers = [
            u.login_name
            for u in db.session.query(User.login_name)
            .filter(User.is_manager == True)
            .limit(3)
            .all()
        ]
    return jsonify(
        {
            "has_users": has_users,
            "sample_managers": sample_managers,
        }
    )



@bp.post("/master-data/import")
def admin_import_master_data():
    """
    Import XLSX (clears documents and master data).
    Requires a valid JWT token only if managers exist.
    """
    # Authorization logic
    auth_ok = False
    if not _has_managers():
        auth_ok = True
    else:
        # Check for emergency token
        admin_token = current_app.config.get("ADMIN_IMPORT_TOKEN")
        header_token = request.headers.get("X-Admin-Import-Token")
        if admin_token and header_token == admin_token:
            auth_ok = True
        else:
            try:
                verify_jwt_in_request(optional=False)
                user = current_user()
                if user and user.is_manager:
                    auth_ok = True
            except JWTExtendedException:
                pass
    
    if not auth_ok:
        return jsonify({
            "error": "Authorization required. Please sign in as a manager to import master data."
        }), 401

    if "file" not in request.files:
        return jsonify({"error": "file required"}), 400
    f = request.files["file"]
    raw = f.read()
    if not raw:
        return jsonify({"error": "empty file"}), 400

    try:
        # We perform the import in a single transaction.
        # import_master_data_xlsx does NOT commit internally now.
        stats = import_master_data_xlsx(raw)
        db.session.commit()
    except Exception as exc:  # noqa: BLE001
        db.session.rollback()
        return jsonify({"error": f"Import failed: {exc}"}), 400

    try:
        logins = [
            row[0]
            for row in db.session.query(User.login_name)
            .order_by(User.login_name)
            .limit(15)
            .all()
        ]
        stats["sample_login_names"] = logins
    except Exception:
        stats["sample_login_names"] = []

    return jsonify(stats), 200

