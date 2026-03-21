"""
Database utility functions.
Centralizes common database operations for consistency.
"""

from typing import Any, Dict, Optional, List
from flask import current_app
from sqlalchemy.exc import SQLAlchemyError
from app.extensions import db


class DatabaseError(Exception):
    """Custom database error exception."""
    pass


def handle_database_error(error: Exception, operation: str = "database operation"):
    """Standardized database error handling."""
    db.session.rollback()
    current_app.logger.error(f"Database error during {operation}: {str(error)}")
    
    if isinstance(error, SQLAlchemyError):
        current_app.logger.error(f"SQLAlchemy error: {error.__class__.__name__}")
    
    raise DatabaseError(f"Database {operation} failed")


def safe_commit(operation: str = "commit") -> bool:
    """Safely commit database transaction."""
    try:
        db.session.commit()
        return True
    except Exception as e:
        handle_database_error(e, operation)
        return False


def safe_add(model_instance, operation: str = "add") -> bool:
    """Safely add model instance to database."""
    try:
        db.session.add(model_instance)
        db.session.flush()  # Get ID without committing
        return True
    except Exception as e:
        handle_database_error(e, operation)
        return False


def safe_delete(model_instance, operation: str = "delete") -> bool:
    """Safely delete model instance from database."""
    try:
        db.session.delete(model_instance)
        db.session.flush()
        return True
    except Exception as e:
        handle_database_error(e, operation)
        return False


def get_by_id(model_class: Any, record_id: int) -> Optional[Any]:
    """Get record by ID safely."""
    try:
        return model_class.query.get(record_id)
    except Exception as e:
        handle_database_error(e, f"get {model_class.__name__}")
        return None


def get_all(model_class: Any, limit: Optional[int] = None) -> List[Any]:
    """Get all records safely."""
    try:
        query = model_class.query
        if limit:
            query = query.limit(limit)
        return query.all()
    except Exception as e:
        handle_database_error(e, f"get all {model_class.__name__}")
        return []


def count_records(model_class: Any) -> int:
    """Count records safely."""
    try:
        return model_class.query.count()
    except Exception as e:
        handle_database_error(e, f"count {model_class.__name__}")
        return 0


def paginate_query(query, page: int = 1, per_page: int = 20):
    """Paginate query safely."""
    try:
        return query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
    except Exception as e:
        handle_database_error(e, "paginate")
        return None
