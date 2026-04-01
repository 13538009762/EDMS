from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required

from app.models import User
from app.utils.auth import current_user

bp = Blueprint("users", __name__)


@bp.get("")
@jwt_required()
def list_users():
    if not current_user():
        return jsonify({"error": "Unauthorized"}), 401
    rows = User.query.order_by(User.login_name).all()
    return jsonify(
        {
            "items": [
                {"id": u.id, "login_name": u.login_name, "display_name": u.display_name()}
                for u in rows
            ]
        }
    )
