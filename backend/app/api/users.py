from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from sqlalchemy import select

from app.models import User, Document, DocumentPermission, ApprovalParticipant, ApprovalFlow
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


@bp.get("/me")
@jwt_required()
def get_current_user():
    user = current_user()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401
    department_name = None
    if user.department:
        department_name = user.department.name
    return jsonify(
        {
            "id": user.id,
            "last_name": user.last_name,
            "first_name": user.first_name,
            "login_name": user.login_name,
            "employee_no": user.employee_no,
            "department_name": department_name,
            "position_short": user.position_short,
        }
    )


@bp.get("/me/stats")
@jwt_required()
def get_user_stats():
    user = current_user()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401
    
    # 统计创建的文档数
    created_docs = Document.query.filter_by(owner_id=user.id).count()
    
    # 统计协作的文档数（通过权限）
    perm_docs = select(DocumentPermission.document_id).where(DocumentPermission.user_id == user.id)
    collab_docs = Document.query.filter(Document.id.in_(perm_docs)).count()
    
    # 统计已批准的文档数
    approved_docs = Document.query.filter_by(status="approved").count()
    
    return jsonify(
        {
            "created_docs": created_docs,
            "collaborated_docs": collab_docs,
            "approved_docs": approved_docs,
        }
    )
