"""
Production-ready database utility functions.
Centralized, secure, and efficient database operations.
"""

from typing import Any, Dict, List, Optional, Tuple
from flask import current_app
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Query
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
        current_app.logger.debug(f"Database commit successful: {operation}")
        return True
    except Exception as e:
        handle_database_error(e, operation)
        return False


def safe_add(model_instance, operation: str = "add") -> bool:
    """Safely add model instance to database."""
    try:
        db.session.add(model_instance)
        db.session.flush()  # Get ID without committing
        current_app.logger.debug(f"Database add successful: {operation}")
        return True
    except Exception as e:
        handle_database_error(e, operation)
        return False


def safe_update(model_instance, operation: str = "update") -> bool:
    """Safely update model instance in database."""
    try:
        db.session.merge(model_instance)
        db.session.flush()
        current_app.logger.debug(f"Database update successful: {operation}")
        return True
    except Exception as e:
        handle_database_error(e, operation)
        return False


def safe_delete(model_instance, operation: str = "delete") -> bool:
    """Safely delete model instance from database."""
    try:
        db.session.delete(model_instance)
        db.session.flush()
        current_app.logger.debug(f"Database delete successful: {operation}")
        return True
    except Exception as e:
        handle_database_error(e, operation)
        return False


def get_by_id(model_class: Any, record_id: int) -> Optional[Any]:
    """Get record by ID safely."""
    try:
        result = model_class.query.get(record_id)
        if result:
            current_app.logger.debug(f"Retrieved {model_class.__name__} ID {record_id}")
        return result
    except Exception as e:
        handle_database_error(e, f"get {model_class.__name__}")
        return None


def get_all(model_class: Any, limit: Optional[int] = None) -> List[Any]:
    """Get all records safely."""
    try:
        query = model_class.query
        if limit:
            query = query.limit(limit)
        results = query.all()
        current_app.logger.debug(f"Retrieved {len(results)} {model_class.__name__} records")
        return results
    except Exception as e:
        handle_database_error(e, f"get all {model_class.__name__}")
        return []


def count_records(model_class: Any) -> int:
    """Count records safely."""
    try:
        count = model_class.query.count()
        current_app.logger.debug(f"Counted {count} {model_class.__name__} records")
        return count
    except Exception as e:
        handle_database_error(e, f"count {model_class.__name__}")
        return 0


def paginate_query(query: Query, page: int = 1, per_page: int = 20) -> Optional[Any]:
    """Paginate query safely."""
    try:
        # Validate pagination parameters
        page = max(1, page)
        per_page = max(1, min(per_page, 100))
        
        paginated = query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        current_app.logger.debug(f"Paginated query: page {page}, per_page {per_page}, total {paginated.total}")
        return paginated
        
    except Exception as e:
        handle_database_error(e, "paginate")
        return None


def create_paginated_response(paginated_query) -> Dict[str, Any]:
    """Create standardized paginated response."""
    if not paginated_query:
        return {
            "items": [],
            "pagination": {
                "page": 1,
                "per_page": 20,
                "total": 0,
                "pages": 0,
                "has_next": False,
                "has_prev": False
            }
        }
    
    return {
        "items": [item.to_dict() if hasattr(item, 'to_dict') else item for item in paginated_query.items],
        "pagination": {
            "page": paginated_query.page,
            "per_page": paginated_query.per_page,
            "total": paginated_query.total,
            "pages": paginated_query.pages,
            "has_next": paginated_query.has_next,
            "has_prev": paginated_query.has_prev
        }
    }


def execute_raw_query(query: str, params: Dict = None) -> List[Any]:
    """Execute raw SQL query safely."""
    try:
        result = db.session.execute(query, params or {})
        records = result.fetchall()
        current_app.logger.debug(f"Executed raw query: {len(records)} records returned")
        return records
    except Exception as e:
        handle_database_error(e, "raw query execution")
        return []


def check_connection() -> bool:
    """Check database connection health."""
    try:
        from sqlalchemy import text
        db.session.execute(text("SELECT 1"))
        current_app.logger.debug("Database connection check: OK")
        return True
    except Exception as e:
        current_app.logger.error(f"Database connection check failed: {str(e)}")
        return False
