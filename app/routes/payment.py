from datetime import datetime

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from app.jwt_utils import get_jwt_identity

from app.extensions import db
from app.middleware.rbac import roles_allowed
from app.models.audit import AuditLog
from app.models.case import Case
from app.models.payment import Payment

payment_bp = Blueprint("payment", __name__)


@payment_bp.route("/create", methods=["POST"])
@jwt_required()
@roles_allowed("lawyer", "admin", "citizen")
def create():
    """Create a payment record"""
    try:
        identity = get_jwt_identity()
        data = request.json or {}
        
        case_id = data.get("case_id")
        amount = data.get("amount")
        
        if not all([case_id, amount]):
            return jsonify({
                "message": "case_id and amount are required",
                "success": False
            }), 400
        
        # Validate case exists
        case = Case.query.get(case_id)
        if not case:
            return jsonify({"message": "Case not found", "success": False}), 404
        
        try:
            amount = float(amount)
            if amount <= 0:
                raise ValueError("Amount must be positive")
        except (ValueError, TypeError):
            return jsonify({
                "message": "Invalid amount format",
                "success": False
            }), 400
        
        payment = Payment(
            case_id=case_id,
            amount=amount,
            currency=data.get("currency", "USD"),
            status=data.get("status", "pending"),
            provider=data.get("provider"),
            provider_ref=data.get("provider_ref")
        )
        db.session.add(payment)
        db.session.flush()
        
        db.session.add(
            AuditLog(
                user_id=identity.get("id"),
                action="Created Payment",
                case_id=case_id,
                details={"payment_id": payment.id, "amount": amount}
            )
        )
        db.session.commit()
        
        return jsonify({
            "message": "Payment record created successfully",
            "success": True,
            "payment": {
                "id": payment.id,
                "case_id": payment.case_id,
                "amount": payment.amount,
                "status": payment.status,
                "created_at": payment.created_at.isoformat()
            }
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Error creating payment: {str(e)}", "success": False}), 500


@payment_bp.route("/<int:payment_id>", methods=["GET"])
@jwt_required()
def get_payment(payment_id):
    """Get a payment record"""
    try:
        payment = Payment.query.get(payment_id)
        if not payment:
            return jsonify({"message": "Payment not found", "success": False}), 404
        
        return jsonify({
            "success": True,
            "payment": {
                "id": payment.id,
                "case_id": payment.case_id,
                "amount": payment.amount,
                "currency": payment.currency,
                "status": payment.status,
                "provider": payment.provider,
                "created_at": payment.created_at.isoformat()
            }
        }), 200
    except Exception as e:
        return jsonify({"message": f"Error fetching payment: {str(e)}", "success": False}), 500


@payment_bp.route("/<int:payment_id>", methods=["PUT"])
@jwt_required()
@roles_allowed("admin", "lawyer")
def update_payment(payment_id):
    """Update payment status"""
    try:
        identity = get_jwt_identity()
        payment = Payment.query.get(payment_id)
        
        if not payment:
            return jsonify({"message": "Payment not found", "success": False}), 404
        
        data = request.json or {}
        
        if "status" in data:
            valid_status = ["pending", "completed", "failed", "refunded"]
            if data["status"] in valid_status:
                payment.status = data["status"]
        
        if "provider_ref" in data:
            payment.provider_ref = data["provider_ref"]
        
        db.session.add(
            AuditLog(
                user_id=identity.get("id"),
                action="Updated Payment",
                case_id=payment.case_id,
                details={"payment_id": payment_id, "new_status": payment.status}
            )
        )
        db.session.commit()
        
        return jsonify({
            "message": "Payment updated successfully",
            "success": True,
            "payment": {
                "id": payment.id,
                "status": payment.status,
                "updated_at": datetime.utcnow().isoformat()
            }
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Error updating payment: {str(e)}", "success": False}), 500


@payment_bp.route("/case/<int:case_id>", methods=["GET"])
@jwt_required()
def get_case_payments(case_id):
    """Get all payments for a case"""
    try:
        Case.query.get_or_404(case_id)
        payments = Payment.query.filter_by(case_id=case_id).all()
        
        total = sum(p.amount for p in payments)
        
        return jsonify({
            "success": True,
            "case_id": case_id,
            "total_amount": total,
            "count": len(payments),
            "payments": [
                {
                    "id": p.id,
                    "amount": p.amount,
                    "status": p.status,
                    "created_at": p.created_at.isoformat()
                }
                for p in payments
            ]
        }), 200
    except Exception as e:
        return jsonify({"message": f"Error fetching payments: {str(e)}", "success": False}), 500
