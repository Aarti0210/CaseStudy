import os
import uuid
from datetime import datetime

from flask import Blueprint, current_app, jsonify, request
from flask_jwt_extended import jwt_required
from app.jwt_utils import get_jwt_identity
from werkzeug.utils import secure_filename

from app.extensions import db
from app.middleware.rbac import roles_allowed
from app.models.audit import AuditLog
from app.models.case import Case
from app.models.document import Document

document_bp = Blueprint("document", __name__)

ALLOWED_EXT = set(["pdf", "png", "jpg", "jpeg", "doc", "docx"])


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXT


@document_bp.route("/upload", methods=["POST"])
@jwt_required()
@roles_allowed("lawyer", "citizen", "judge", "admin")
def upload():
    """Upload a document"""
    try:
        if "file" not in request.files:
            return jsonify({"message": "file field is required", "success": False}), 400
        
        f = request.files["file"]
        if f.filename == "":
            return jsonify({"message": "No file selected", "success": False}), 400
        
        if not allowed_file(f.filename):
            return jsonify({
                "message": f"File type not allowed. Allowed: {', '.join(ALLOWED_EXT)}",
                "success": False
            }), 400
        
        case_id = request.form.get("case_id")
        if not case_id:
            return jsonify({"message": "case_id is required", "success": False}), 400
        
        # Validate case exists
        case = Case.query.get(case_id)
        if not case:
            return jsonify({"message": "Case not found", "success": False}), 404
        
        filename = secure_filename(f.filename)
        unique_name = f"{uuid.uuid4().hex}_{filename}"
        upload_folder = current_app.config.get("UPLOAD_FOLDER", "uploads")
        os.makedirs(upload_folder, exist_ok=True)
        dest = os.path.join(upload_folder, unique_name)
        
        f.save(dest)
        file_size = os.path.getsize(dest)
        
        # Check file size limit (default 16MB)
        max_size = current_app.config.get("MAX_CONTENT_LENGTH", 16 * 1024 * 1024)
        if file_size > max_size:
            os.remove(dest)
            return jsonify({
                "message": f"File too large (max {max_size // 1024 // 1024}MB)",
                "success": False
            }), 413
        
        identity = get_jwt_identity()
        doc = Document(
            case_id=case_id,
            filename=unique_name,
            original_name=filename,
            content_type=f.content_type,
            size=file_size,
            uploaded_by=identity.get("id"),
        )
        db.session.add(doc)
        db.session.flush()
        
        db.session.add(
            AuditLog(
                user_id=identity.get("id"),
                action="Uploaded Document",
                case_id=case_id,
                details={"document_id": doc.id, "filename": filename, "size": file_size}
            )
        )
        db.session.commit()
        
        return jsonify({
            "message": "Document uploaded successfully",
            "success": True,
            "document": {
                "id": doc.id,
                "filename": unique_name,
                "original_name": filename,
                "size": file_size,
                "uploaded_at": doc.uploaded_at.isoformat()
            }
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Error uploading document: {str(e)}", "success": False}), 500


@document_bp.route("/<int:case_id>", methods=["GET"])
@jwt_required()
def get_case_documents(case_id):
    """Get all documents for a case"""
    try:
        Case.query.get_or_404(case_id)
        docs = Document.query.filter_by(case_id=case_id).all()
        
        return jsonify({
            "success": True,
            "case_id": case_id,
            "count": len(docs),
            "documents": [
                {
                    "id": d.id,
                    "original_name": d.original_name,
                    "filename": d.filename,
                    "size": d.size,
                    "content_type": d.content_type,
                    "uploaded_at": d.uploaded_at.isoformat(),
                    "uploaded_by": d.uploaded_by
                }
                for d in docs
            ]
        }), 200
    except Exception as e:
        return jsonify({"message": f"Error fetching documents: {str(e)}", "success": False}), 500


@document_bp.route("/<int:doc_id>", methods=["DELETE"])
@jwt_required()
@roles_allowed("lawyer", "admin")
def delete_document(doc_id):
    """Delete a document"""
    try:
        identity = get_jwt_identity()
        doc = Document.query.get(doc_id)
        
        if not doc:
            return jsonify({"message": "Document not found", "success": False}), 404
        
        # Try to delete file
        upload_folder = current_app.config.get("UPLOAD_FOLDER", "uploads")
        file_path = os.path.join(upload_folder, doc.filename)
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception:
                pass  # Continue even if file deletion fails
        
        case_id = doc.case_id
        db.session.delete(doc)
        db.session.add(
            AuditLog(
                user_id=identity.get("id"),
                action="Deleted Document",
                case_id=case_id,
                details={"document_id": doc_id, "filename": doc.original_name}
            )
        )
        db.session.commit()
        
        return jsonify({
            "message": "Document deleted successfully",
            "success": True,
            "document_id": doc_id
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Error deleting document: {str(e)}", "success": False}), 500
