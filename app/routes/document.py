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
from app.utils.api_response import success_response, error_response
from app.utils.pagination import get_pagination_params, paginate_query, create_paginated_response

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
            return error_response("file field is required", 400)
        
        f = request.files["file"]
        if f.filename == "":
            return error_response("No file selected", 400)
        
        if not allowed_file(f.filename):
            return error_response(
                f"File type not allowed. Allowed: {', '.join(ALLOWED_EXT)}", 400
            )
        
        case_id = request.form.get("case_id")
        if not case_id:
            return error_response("case_id is required", 400)
        
        # Validate case exists
        case = Case.query.get(case_id)
        if not case:
            return error_response("Case not found", 404)
        
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
            return error_response(
                f"File too large (max {max_size // 1024 // 1024}MB)", 413
            )
        
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
        
        return success_response(
            data={
                "document": {
                    "id": doc.id,
                    "filename": unique_name,
                    "original_name": filename,
                    "size": file_size,
                    "uploaded_at": doc.uploaded_at.isoformat(),
                }
            },
            message="Document uploaded successfully",
            status_code=201,
        )
    except Exception as e:
        db.session.rollback()
        return error_response(f"Error uploading document: {str(e)}", 500)


@document_bp.route("/<int:case_id>", methods=["GET"])
@jwt_required()
def get_case_documents(case_id):
    """Get all documents for a case with pagination"""
    try:
        Case.query.get_or_404(case_id)
        
        # Get pagination parameters
        limit, offset = get_pagination_params()
        
        # Build query
        query = Document.query.filter_by(case_id=case_id).order_by(
            Document.uploaded_at.desc()
        )
        
        # Apply pagination
        documents, pagination_metadata = paginate_query(query, limit, offset)
        
        # Format response data
        documents_data = [
            {
                "id": d.id,
                "original_name": d.original_name,
                "filename": d.filename,
                "size": d.size,
                "content_type": d.content_type,
                "uploaded_at": d.uploaded_at.isoformat(),
                "uploaded_by": d.uploaded_by,
            }
            for d in documents
        ]
        
        paginated_data = create_paginated_response(documents_data, pagination_metadata)
        
        return success_response(
            data={
                "case_id": case_id,
                **paginated_data
            },
            message=f"Retrieved {len(documents)} documents"
        )
    except Exception as e:
        return error_response(f"Error fetching documents: {str(e)}", 500)


@document_bp.route("/<int:doc_id>", methods=["DELETE"])
@jwt_required()
@roles_allowed("lawyer", "admin")
def delete_document(doc_id):
    """Delete a document"""
    try:
        identity = get_jwt_identity()
        doc = Document.query.get(doc_id)
        
        if not doc:
            return error_response("Document not found", 404)
        
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
        
        return success_response(
            data={"document_id": doc_id}, message="Document deleted successfully"
        )
    except Exception as e:
        db.session.rollback()
        return error_response(f"Error deleting document: {str(e)}", 500)
