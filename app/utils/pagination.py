from typing import Dict, Any, Tuple, Optional
from flask import request
from sqlalchemy.orm import Query


def get_pagination_params() -> Tuple[int, int]:
    """Extract pagination parameters from request query string."""
    try:
        limit = min(int(request.args.get('limit', 20)), 100)  # Cap at 100 for safety
        offset = max(int(request.args.get('offset', 0)), 0)
    except (ValueError, TypeError):
        limit = 20
        offset = 0
    
    return limit, offset


def paginate_query(query: Query, limit: int = 20, offset: int = 0) -> Tuple[list, Dict[str, Any]]:
    """
    Paginate a SQLAlchemy query and return items with pagination metadata.
    
    Args:
        query: SQLAlchemy query object
        limit: Number of items per page
        offset: Number of items to skip
        
    Returns:
        Tuple of (items, pagination_metadata)
    """
    total = query.count()
    items = query.offset(offset).limit(limit).all()
    
    pagination_metadata = {
        'total': total,
        'limit': limit,
        'offset': offset,
        'has_next': offset + limit < total,
        'has_prev': offset > 0,
        'next_offset': offset + limit if offset + limit < total else None,
        'prev_offset': max(offset - limit, 0) if offset > 0 else None
    }
    
    return items, pagination_metadata


def create_paginated_response(items: list, pagination_metadata: Dict[str, Any], 
                            message: Optional[str] = None) -> Dict[str, Any]:
    """Create a standardized paginated response."""
    response_data = {
        'items': items,
        'pagination': pagination_metadata
    }
    
    return response_data
