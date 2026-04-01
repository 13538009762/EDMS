"""Documents REST API."""
from __future__ import annotations

import base64
import json
from datetime import datetime

from flask import Blueprint, Response, jsonify, request
from flask_jwt_extended import jwt_required

from app.extensions import db
from sqlalchemy import or_, select

from app.models import (
    ApprovalFlow,
    Document,
    DocumentPermission,
    DocumentVersion,
    User,
)
from app.models.workflow import ApprovalParticipant
from app.services.approval_service import start_flow
from app.services.diff_service import diff_html
from app.services.document_access import (
    user_can_comment,
    user_can_edit_content,
    user_can_edit_metadata,
    user_can_view_document,
    user_effective_document_role,
)
from app.services.document_state import VALID_STATUSES
from app.services.export_service import export_docx_bytes, export_pdf_bytes
from app.utils.auth import current_user

bp = Blueprint("documents", __name__)


def _doc_to_summary(doc: Document, user: User) -> dict:
    ver = doc.current_version
    return {
        "id": doc.id,
        "title": doc.title,
        "status": doc.status,
        "owner_id": doc.owner_id,
        "is_owner": doc.owner_id == user.id,
        "my_role": user_effective_document_role(user, doc),
        "created_at": doc.created_at.isoformat() if doc.created_at else None,
        "updated_at": doc.updated_at.isoformat() if doc.updated_at else None,
        "current_version_id": doc.current_version_id,
        "version_no": ver.version_no if ver else None,
        "can_view": True,
        "can_edit": user_can_edit_content(user, doc),
        "can_comment": user_can_comment(user, doc),
        "can_manage_permissions": doc.owner_id == user.id,
    }


@bp.get("")
@jwt_required()
def list_documents():
    user = current_user()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401
    scope = request.args.get("scope", "mine")
    status_filter = request.args.get("status")
    q = Document.query
    if status_filter:
        if status_filter not in VALID_STATUSES:
            return jsonify({"error": "invalid status filter"}), 400
        q = q.filter(Document.status == status_filter)
    if scope == "approved":
        q = q.filter(Document.status == "approved")
    else:
        perm_ids = select(DocumentPermission.document_id).where(
            DocumentPermission.user_id == user.id
        )
        flow_ids = (
            select(ApprovalFlow.document_id)
            .join(ApprovalParticipant, ApprovalParticipant.flow_id == ApprovalFlow.id)
            .where(ApprovalParticipant.user_id == user.id)
        )
        q = q.filter(
            or_(
                Document.owner_id == user.id,
                Document.status == "approved",
                Document.id.in_(perm_ids),
                Document.id.in_(flow_ids),
            )
        )
    docs = q.order_by(Document.updated_at.desc()).all()
    return jsonify({"items": [_doc_to_summary(d, user) for d in docs]})


@bp.post("")
@jwt_required()
def create_document():
    user = current_user()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401
    data = request.get_json(silent=True) or {}
    title = (data.get("title") or "Untitled").strip()[:512]
    doc = Document(owner_id=user.id, title=title, status="draft")
    db.session.add(doc)
    db.session.flush()
    ver = DocumentVersion(
        document_id=doc.id,
        version_no=1,
        content_json=DocumentVersion.default_content_json(),
        created_by_id=user.id,
    )
    db.session.add(ver)
    db.session.flush()
    doc.current_version_id = ver.id
    db.session.commit()
    return jsonify(_doc_to_summary(doc, user)), 201


@bp.get("/<int:doc_id>")
@jwt_required()
def get_document(doc_id: int):
    user = current_user()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401
    doc = db.session.get(Document, doc_id)
    if not doc or not user_can_view_document(user, doc):
        return jsonify({"error": "Not found"}), 404
    ver = doc.current_version
    body = {
        **_doc_to_summary(doc, user),
        "owner_login": doc.owner.login_name if doc.owner else None,
        "page_settings_json": doc.page_settings_json,
        "content_json": ver.content_json if ver else None,
        "yjs_state_b64": base64.b64encode(ver.yjs_state).decode("ascii")
        if ver and ver.yjs_state
        else None,
    }
    return jsonify(body)


@bp.patch("/<int:doc_id>")
@jwt_required()
def patch_document(doc_id: int):
    user = current_user()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401
    doc = db.session.get(Document, doc_id)
    if not doc or not user_can_view_document(user, doc):
        return jsonify({"error": "Not found"}), 404
    data = request.get_json(silent=True) or {}
    if "title" in data:
        if not user_can_edit_metadata(user, doc):
            return jsonify({"error": "Forbidden: cannot edit title in current state/role"}), 403
        doc.title = str(data["title"])[:512]
    if "page_settings_json" in data:
        if not user_can_edit_metadata(user, doc):
            return jsonify({"error": "Forbidden: cannot edit page settings"}), 403
        doc.page_settings_json = data["page_settings_json"]
    doc.updated_at = datetime.utcnow()
    db.session.commit()
    return jsonify(_doc_to_summary(doc, user))


@bp.put("/<int:doc_id>/content")
@jwt_required()
def put_content(doc_id: int):
    """Autosave document body (TipTap JSON + optional Yjs state)."""
    user = current_user()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401
    doc = db.session.get(Document, doc_id)
    if not doc or not user_can_view_document(user, doc):
        return jsonify({"error": "Not found"}), 404
    if not user_can_edit_content(user, doc):
        return jsonify({"error": "Forbidden"}), 403
    data = request.get_json(silent=True) or {}
    ver = doc.current_version
    if not ver:
        return jsonify({"error": "No version"}), 400
    if "content_json" in data:
        cj = data["content_json"]
        ver.content_json = json.dumps(cj) if isinstance(cj, (dict, list)) else str(cj)
    if "yjs_state_b64" in data and data["yjs_state_b64"]:
        ver.yjs_state = base64.b64decode(data["yjs_state_b64"])
    doc.updated_at = datetime.utcnow()
    db.session.commit()
    return jsonify({"ok": True})


@bp.get("/<int:doc_id>/versions")
@jwt_required()
def list_versions(doc_id: int):
    user = current_user()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401
    doc = db.session.get(Document, doc_id)
    if not doc or not user_can_view_document(user, doc):
        return jsonify({"error": "Not found"}), 404
    items = []
    for v in sorted(doc.versions, key=lambda x: x.version_no):
        items.append(
            {
                "id": v.id,
                "version_no": v.version_no,
                "created_at": v.created_at.isoformat() if v.created_at else None,
                "parent_version_id": v.parent_version_id,
                "created_by_id": v.created_by_id,
            }
        )
    return jsonify({"items": items})


@bp.get("/<int:doc_id>/versions/<int:vid>/content")
@jwt_required()
def get_version_content(doc_id: int, vid: int):
    user = current_user()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401
    doc = db.session.get(Document, doc_id)
    if not doc or not user_can_view_document(user, doc):
        return jsonify({"error": "Not found"}), 404
    v = db.session.get(DocumentVersion, vid)
    if not v or v.document_id != doc.id:
        return jsonify({"error": "Not found"}), 404
    return jsonify(
        {
            "content_json": v.content_json,
            "version_no": v.version_no,
        }
    )


@bp.get("/<int:doc_id>/diff")
@jwt_required()
def get_diff(doc_id: int):
    user = current_user()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401
    doc = db.session.get(Document, doc_id)
    if not doc or not user_can_view_document(user, doc):
        return jsonify({"error": "Not found"}), 404
    v_from = request.args.get("from", type=int)
    v_to = request.args.get("to", type=int)
    if not v_from or not v_to:
        return jsonify({"error": "from and to version ids required"}), 400
    a = db.session.get(DocumentVersion, v_from)
    b = db.session.get(DocumentVersion, v_to)
    if not a or not b or a.document_id != doc.id or b.document_id != doc.id:
        return jsonify({"error": "Invalid versions"}), 400
    html = diff_html(a.content_json or "{}", b.content_json or "{}")
    return jsonify({"html": html})


@bp.post("/<int:doc_id>/permissions")
@jwt_required()
def set_permissions(doc_id: int):
    user = current_user()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401
    doc = db.session.get(Document, doc_id)
    if not doc or doc.owner_id != user.id:
        return jsonify({"error": "Forbidden"}), 403
    if doc.status != "draft":
        return jsonify({"error": "Permissions can only be changed while document is draft"}), 400
    data = request.get_json(silent=True) or {}
    grants = data.get("grants") or []
    seen: set[int] = set()
    DocumentPermission.query.filter_by(document_id=doc.id).delete()
    for g in grants:
        uid = g.get("user_id")
        role = g.get("role")
        if not uid or role not in ("view", "edit", "comment"):
            continue
        uid_int = int(uid)
        if uid_int == user.id:
            continue
        if uid_int in seen:
            continue
        seen.add(uid_int)
        if not db.session.get(User, uid_int):
            return jsonify({"error": f"Unknown user_id: {uid_int}"}), 400
        db.session.add(
            DocumentPermission(document_id=doc.id, user_id=uid_int, role=role),
        )
    db.session.commit()
    return jsonify({"ok": True})


@bp.delete("/<int:doc_id>/permissions/<int:grantee_id>")
@jwt_required()
def delete_permission(doc_id: int, grantee_id: int):
    user = current_user()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401
    doc = db.session.get(Document, doc_id)
    if not doc or doc.owner_id != user.id:
        return jsonify({"error": "Forbidden"}), 403
    if doc.status != "draft":
        return jsonify({"error": "Permissions can only be changed while document is draft"}), 400
    p = DocumentPermission.query.filter_by(
        document_id=doc.id, user_id=grantee_id
    ).first()
    if not p:
        return jsonify({"error": "Not found"}), 404
    db.session.delete(p)
    db.session.commit()
    return jsonify({"ok": True})


@bp.get("/<int:doc_id>/permissions")
@jwt_required()
def get_permissions(doc_id: int):
    user = current_user()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401
    doc = db.session.get(Document, doc_id)
    if not doc or doc.owner_id != user.id:
        return jsonify({"error": "Not found"}), 404
    perms = DocumentPermission.query.filter_by(document_id=doc.id).all()
    return jsonify(
        {
            "items": [
                {"user_id": p.user_id, "role": p.role, "login_name": p.user.login_name}
                for p in perms
            ]
        }
    )


@bp.get("/<int:doc_id>/export.docx")
@jwt_required()
def export_docx(doc_id: int):
    user = current_user()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401
    doc = db.session.get(Document, doc_id)
    if not doc or not user_can_view_document(user, doc):
        return jsonify({"error": "Not found"}), 404
    ver = doc.current_version
    raw = export_docx_bytes(ver.content_json if ver else "{}")
    return Response(
        raw,
        mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": f'attachment; filename="doc_{doc_id}.docx"'},
    )


@bp.get("/<int:doc_id>/export.pdf")
@jwt_required()
def export_pdf(doc_id: int):
    user = current_user()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401
    doc = db.session.get(Document, doc_id)
    if not doc or not user_can_view_document(user, doc):
        return jsonify({"error": "Not found"}), 404
    ver = doc.current_version
    raw = export_pdf_bytes(ver.content_json if ver else "{}")
    return Response(
        raw,
        mimetype="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="doc_{doc_id}.pdf"'},
    )


@bp.post("/<int:doc_id>/approval")
@jwt_required()
def start_approval(doc_id: int):
    user = current_user()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401
    doc = db.session.get(Document, doc_id)
    if not doc or doc.owner_id != user.id:
        return jsonify({"error": "Forbidden"}), 403
    data = request.get_json(silent=True) or {}
    flow_type = (data.get("flow_type") or "parallel").lower()
    ids = data.get("approver_ids") or []
    if flow_type not in ("parallel", "sequential"):
        return jsonify({"error": "invalid flow_type"}), 400
    approvers = [int(x) for x in ids]
    try:
        flow = start_flow(doc, flow_type, approvers)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    db.session.commit()
    return jsonify({"flow_id": flow.id, "document_status": doc.status})


@bp.post("/<int:doc_id>/new-version")
@jwt_required()
def new_version_after_reject(doc_id: int):
    """Create new version from current content when document was rejected."""
    user = current_user()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401
    doc = db.session.get(Document, doc_id)
    if not doc or doc.owner_id != user.id:
        return jsonify({"error": "Forbidden"}), 403
    if doc.status != "rejected":
        return jsonify({"error": "Only rejected documents"}), 400
    old = doc.current_version
    max_no = max((v.version_no for v in doc.versions), default=0)
    ver = DocumentVersion(
        document_id=doc.id,
        version_no=max_no + 1,
        content_json=old.content_json if old else DocumentVersion.default_content_json(),
        yjs_state=old.yjs_state if old else None,
        created_by_id=user.id,
        parent_version_id=old.id if old else None,
    )
    db.session.add(ver)
    db.session.flush()
    doc.current_version_id = ver.id
    doc.status = "draft"
    doc.updated_at = datetime.utcnow()
    db.session.commit()
    return jsonify({"current_version_id": ver.id, "version_no": ver.version_no})
