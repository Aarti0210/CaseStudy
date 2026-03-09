from datetime import datetime, timedelta

from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from sqlalchemy import func

from app.extensions import db
from app.middleware.rbac import role_required
from app.models.case import Case
from app.models.payment import Payment
from app.models.user import User
from app.models.hearing import Hearing
from app.models.document import Document
from app.models.ai_log import AILog
from app.models.audit import AuditLog

admin_bp = Blueprint("admin", __name__)


@admin_bp.route("/analytics", methods=["GET"])
@jwt_required()
@role_required("admin")
def analytics():
    """Comprehensive analytics dashboard with AI, judge workload, delays, payments"""
    now = datetime.utcnow()
    week_ago = now - timedelta(days=7)
    month_ago = now - timedelta(days=30)
    
    # === USER & ROLE STATS ===
    total_users = User.query.count()
    # counts by role require joining role table
    from app.models.role import Role
    lawyers = (
        User.query.join(Role).filter(Role.name == "lawyer").count()
    )
    judges = (
        User.query.join(Role).filter(Role.name == "judge").count()
    )
    citizens = (
        User.query.join(Role).filter(Role.name == "citizen").count()
    )
    admins = (
        User.query.join(Role).filter(Role.name == "admin").count()
    )
    active_users = User.query.filter_by(is_active=True).count()
    
    # === CASE STATS ===
    total_cases = Case.query.count()
    active_cases = Case.query.filter_by(status="Active").count()
    pending_cases = Case.query.filter_by(status="Pending").count()
    closed_cases = Case.query.filter_by(status="Closed").count()
    
    # === HEARING STATS ===
    total_hearings = Hearing.query.count()
    scheduled_hearings = Hearing.query.filter_by(status="Scheduled").count()
    completed_hearings = Hearing.query.filter_by(status="Completed").count()
    postponed_hearings = Hearing.query.filter_by(status="Postponed").count()
    
    # Upcoming hearings (next 7 days)
    upcoming_hearings = Hearing.query.filter(
        Hearing.hearing_date.between(now, now + timedelta(days=7)),
        Hearing.status.in_(["Scheduled", "Pending"])
    ).count()
    
    # Overdue hearings (past scheduled date but not marked complete)
    overdue_hearings = Hearing.query.filter(
        Hearing.hearing_date < now,
        Hearing.status.in_(["Scheduled", "Pending"])
    ).count()
    
    # === JUDGE WORKLOAD ANALYSIS ===
    judge_workload = []
    # iterate judges via join to Role table
    from app.models.role import Role
    for judge in User.query.join(Role).filter(Role.name == "judge").all():
        upcoming = Hearing.query.filter(
            Hearing.judge_id == judge.id,
            Hearing.hearing_date >= now,
            Hearing.status.in_(["Scheduled", "Pending"])
        ).count()
        completed = Hearing.query.filter(
            Hearing.judge_id == judge.id,
            Hearing.status == "Completed"
        ).count()
        judge_workload.append({
            "judge_id": judge.id,
            "name": judge.name,
            "upcoming_hearings": upcoming,
            "completed_hearings": completed,
            "workload_stress": "High" if upcoming > 10 else "Medium" if upcoming > 5 else "Low"
        })
    
    # === CASE AGE & DELAY ANALYSIS ===
    case_ages = []
    for case in Case.query.all():
        age_days = (now - case.created_at).days
        case_ages.append(age_days)
    
    avg_case_age = sum(case_ages) / len(case_ages) if case_ages else 0
    max_case_age = max(case_ages) if case_ages else 0
    
    # Cases older than 6 months
    old_cases = Case.query.filter(
        Case.created_at < month_ago
    ).count()
    
    # === DOCUMENT STATS ===
    total_documents = Document.query.count()
    total_upload_size = db.session.query(func.sum(Document.size)).scalar() or 0
    
    # Recent uploads (last 7 days)
    recent_uploads = Document.query.filter(
        Document.uploaded_at >= week_ago
    ).count()
    
    # === PAYMENT & REVENUE STATS ===
    total_revenue = db.session.query(func.sum(Payment.amount)).scalar() or 0
    pending_payments = db.session.query(func.sum(Payment.amount)).filter(
        Payment.status == "Pending"
    ).scalar() or 0
    completed_payments = db.session.query(func.sum(Payment.amount)).filter(
        Payment.status == "Completed"
    ).scalar() or 0
    
    # Revenue this month
    revenue_this_month = db.session.query(func.sum(Payment.amount)).filter(
        Payment.created_at >= month_ago,
        Payment.status == "Completed"
    ).scalar() or 0
    
    # Payment count
    total_payment_count = Payment.query.count()
    completed_payment_count = Payment.query.filter_by(status="Completed").count()
    
    # === AI USAGE STATS ===
    total_ai_calls = AILog.query.count()
    ai_calls_this_month = AILog.query.filter(
        AILog.created_at >= month_ago
    ).count()
    
    # Token usage
    total_tokens = db.session.query(func.sum(AILog.total_tokens)).scalar() or 0
    avg_tokens_per_call = (
        total_tokens / total_ai_calls if total_ai_calls > 0 else 0
    )
    
    # AI feature usage breakdown
    ai_features = {}
    for log in AILog.query.all():
        feature = log.feature_used or "unknown"
        ai_features[feature] = ai_features.get(feature, 0) + 1
    
    # Most used AI feature
    most_used_ai_feature = max(ai_features.items(), key=lambda x: x[1])[0] if ai_features else None
    
    # === AUDIT TRAIL STATS ===
    total_audit_logs = AuditLog.query.count()
    audit_logs_this_week = AuditLog.query.filter(
        AuditLog.timestamp >= week_ago
    ).count()
    
    # Most active users (by audit count)
    active_user_stats = db.session.query(
        AuditLog.user_id,
        User.name,
        func.count(AuditLog.id).label("action_count")
    ).join(User, AuditLog.user_id == User.id).group_by(
        AuditLog.user_id, User.name
    ).order_by(func.count(AuditLog.id).desc()).limit(5).all()
    
    most_active_users = [
        {
            "user_id": stat[0],
            "name": stat[1],
            "actions": stat[2]
        }
        for stat in active_user_stats
    ]
    
    # === SYSTEM HEALTH SUMMARY ===
    pending_ratio = (pending_cases / total_cases * 100) if total_cases > 0 else 0
    overdue_ratio = (overdue_hearings / total_hearings * 100) if total_hearings > 0 else 0
    
    system_health = "Excellent" if overdue_ratio < 5 else "Good" if overdue_ratio < 15 else "Fair" if overdue_ratio < 25 else "Critical"
    
    return jsonify(
        {
            "timestamp": now.isoformat(),
            "system_health": system_health,
            
            "users": {
                "total": total_users,
                "active": active_users,
                "by_role": {
                    "admin": admins,
                    "judge": judges,
                    "lawyer": lawyers,
                    "citizen": citizens
                }
            },
            
            "cases": {
                "total": total_cases,
                "by_status": {
                    "active": active_cases,
                    "pending": pending_cases,
                    "closed": closed_cases
                },
                "age_metrics": {
                    "average_age_days": round(avg_case_age, 1),
                    "oldest_case_days": max_case_age,
                    "cases_older_than_6_months": old_cases
                }
            },
            
            "hearings": {
                "total": total_hearings,
                "by_status": {
                    "scheduled": scheduled_hearings,
                    "completed": completed_hearings,
                    "postponed": postponed_hearings
                },
                "upcoming_7_days": upcoming_hearings,
                "overdue": overdue_hearings,
                "overdue_percentage": round(overdue_ratio, 1)
            },
            
            "judge_workload": {
                "total_judges": judges,
                "details": judge_workload,
                "average_workload": round(
                    sum(j["upcoming_hearings"] for j in judge_workload) / judges
                    if judges > 0 else 0, 1
                )
            },
            
            "documents": {
                "total": total_documents,
                "total_size_mb": round(total_upload_size / (1024 * 1024), 2),
                "recent_uploads_7_days": recent_uploads
            },
            
            "payments": {
                "total_revenue": round(total_revenue, 2),
                "completed_revenue": round(completed_payments, 2),
                "pending_revenue": round(pending_payments, 2),
                "monthly_revenue": round(revenue_this_month, 2),
                "payment_count": total_payment_count,
                "completion_rate": round(
                    completed_payment_count / total_payment_count * 100
                    if total_payment_count > 0 else 0, 1
                )
            },
            
            "ai_analytics": {
                "total_calls": total_ai_calls,
                "calls_this_month": ai_calls_this_month,
                "total_tokens_used": total_tokens,
                "avg_tokens_per_call": round(avg_tokens_per_call, 0),
                "most_used_feature": most_used_ai_feature,
                "feature_breakdown": ai_features
            },
            
            "audit": {
                "total_logs": total_audit_logs,
                "logs_this_week": audit_logs_this_week,
                "most_active_users": most_active_users
            }
        }
    )


@admin_bp.route("/ai-costs", methods=["GET"])
@jwt_required()
@role_required("admin")
def ai_cost_analysis():
    """Detailed AI usage and cost analysis"""
    now = datetime.utcnow()
    month_ago = now - timedelta(days=30)
    week_ago = now - timedelta(days=7)
    
    # Token costs (OpenAI pricing ~$0.01 per 1000 tokens for input, $0.03 for output)
    INPUT_COST_PER_1K = 0.01
    OUTPUT_COST_PER_1K = 0.03
    
    # All time
    total_prompt_tokens = db.session.query(
        func.sum(AILog.prompt_tokens)
    ).scalar() or 0
    total_completion_tokens = db.session.query(
        func.sum(AILog.completion_tokens)
    ).scalar() or 0
    
    total_input_cost = (total_prompt_tokens / 1000) * INPUT_COST_PER_1K
    total_output_cost = (total_completion_tokens / 1000) * OUTPUT_COST_PER_1K
    total_ai_cost = total_input_cost + total_output_cost
    
    # This month
    month_prompt_tokens = db.session.query(
        func.sum(AILog.prompt_tokens)
    ).filter(AILog.created_at >= month_ago).scalar() or 0
    month_completion_tokens = db.session.query(
        func.sum(AILog.completion_tokens)
    ).filter(AILog.created_at >= month_ago).scalar() or 0
    
    month_input_cost = (month_prompt_tokens / 1000) * INPUT_COST_PER_1K
    month_output_cost = (month_completion_tokens / 1000) * OUTPUT_COST_PER_1K
    month_ai_cost = month_input_cost + month_output_cost
    
    # This week
    week_prompt_tokens = db.session.query(
        func.sum(AILog.prompt_tokens)
    ).filter(AILog.created_at >= week_ago).scalar() or 0
    week_completion_tokens = db.session.query(
        func.sum(AILog.completion_tokens)
    ).filter(AILog.created_at >= week_ago).scalar() or 0
    
    week_input_cost = (week_prompt_tokens / 1000) * INPUT_COST_PER_1K
    week_output_cost = (week_completion_tokens / 1000) * OUTPUT_COST_PER_1K
    week_ai_cost = week_input_cost + week_output_cost
    
    # Cost by feature
    feature_costs = {}
    for log in AILog.query.filter(AILog.prompt_tokens.isnot(None)).all():
        feature = log.feature_used or "unknown"
        input_cost = (log.prompt_tokens / 1000) * INPUT_COST_PER_1K
        output_cost = (log.completion_tokens / 1000) * OUTPUT_COST_PER_1K
        total_cost = input_cost + output_cost
        
        if feature not in feature_costs:
            feature_costs[feature] = {"cost": 0, "count": 0, "tokens": 0}
        
        feature_costs[feature]["cost"] += total_cost
        feature_costs[feature]["count"] += 1
        feature_costs[feature]["tokens"] += log.prompt_tokens + log.completion_tokens
    
    # Sort by cost
    sorted_features = sorted(
        feature_costs.items(),
        key=lambda x: x[1]["cost"],
        reverse=True
    )
    
    return jsonify({
        "timestamp": now.isoformat(),
        "cost_all_time": {
            "input_cost": round(total_input_cost, 2),
            "output_cost": round(total_output_cost, 2),
            "total_cost": round(total_ai_cost, 2),
            "prompt_tokens": total_prompt_tokens,
            "completion_tokens": total_completion_tokens
        },
        "cost_this_month": {
            "input_cost": round(month_input_cost, 2),
            "output_cost": round(month_output_cost, 2),
            "total_cost": round(month_ai_cost, 2),
            "prompt_tokens": month_prompt_tokens,
            "completion_tokens": month_completion_tokens
        },
        "cost_this_week": {
            "input_cost": round(week_input_cost, 2),
            "output_cost": round(week_output_cost, 2),
            "total_cost": round(week_ai_cost, 2),
            "prompt_tokens": week_prompt_tokens,
            "completion_tokens": week_completion_tokens
        },
        "cost_by_feature": [
            {
                "feature": feature,
                "cost": round(data["cost"], 2),
                "call_count": data["count"],
                "total_tokens": data["tokens"]
            }
            for feature, data in sorted_features
        ]
    })


@admin_bp.route("/case-delays", methods=["GET"])
@jwt_required()
@role_required("admin")
def case_delay_report():
    """Case delay analysis and risk assessment"""
    now = datetime.utcnow()
    month_ago = now - timedelta(days=30)
    quarter_ago = now - timedelta(days=90)
    
    # Delay severity categories
    delays = {
        "critical": [],  # > 1 year
        "high": [],      # 6-12 months (should be a list, not dict)
        "medium": [],    # 3-6 months
        "low": []        # < 3 months
    }
    
    for case in Case.query.all():
        age_days = (now - case.created_at).days
        
        if age_days > 365:
            delays["critical"].append({
                "case_id": case.id,
                "title": case.title,
                "age_days": age_days,
                "status": case.status
            })
        elif age_days > 180:
            delays["high"].append({
                "case_id": case.id,
                "title": case.title,
                "age_days": age_days,
                "status": case.status
            })
        elif age_days > 90:
            delays["medium"].append({
                "case_id": case.id,
                "title": case.title,
                "age_days": age_days,
                "status": case.status
            })
        else:
            delays["low"].append({
                "case_id": case.id,
                "title": case.title,
                "age_days": age_days,
                "status": case.status
            })
    
    # Cases without recent hearing
    stalled_cases = []
    for case in Case.query.all():
        last_hearing = Hearing.query.filter_by(case_id=case.id).order_by(
            Hearing.hearing_date.desc()
        ).first()
        
        if not last_hearing or (now - last_hearing.hearing_date).days > 60:
            hearing_gap_days = (
                (now - last_hearing.hearing_date).days
                if last_hearing else (now - case.created_at).days
            )
            stalled_cases.append({
                "case_id": case.id,
                "title": case.title,
                "days_since_hearing": hearing_gap_days,
                "status": case.status
            })
    
    # Judge with most delayed cases - query via Role join
    from app.models.role import Role
    judge_delay_stats = []
    for judge in User.query.join(Role).filter(Role.name == "judge").all():
        judge_cases = Case.query.filter_by(assigned_judge_id=judge.id).all()
        delayed = len([
            c for c in judge_cases
            if (now - c.created_at).days > 180
        ])
        judge_delay_stats.append({
            "judge_id": judge.id,
            "name": judge.name,
            "assigned_cases": len(judge_cases),
            "delayed_cases": delayed
        })
    
    return jsonify({
        "timestamp": now.isoformat(),
        "delay_summary": {
            "critical": len(delays["critical"]),
            "high": len(delays["high"]),
            "medium": len(delays["medium"]),
            "low": len(delays["low"])
        },
        "critical_cases": delays["critical"][:10],  # Top 10
        "high_risk_cases": delays["high"][:10],  # Fixed: delays["high"] is a list now
        "stalled_cases": stalled_cases[:10],
        "judge_performance": [
            stat for stat in judge_delay_stats
            if stat["delayed_cases"] > 0
        ]  # Only show judges with delays
    })
