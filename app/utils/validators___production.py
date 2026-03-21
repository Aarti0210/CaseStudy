"""
Production-ready input validation utilities.
Comprehensive validation with security and sanitization.
"""

import re
from typing import Any, Dict, List


def validate_email(email: str) -> bool:
    """Validate email format with comprehensive checks."""
    if not isinstance(email, str) or len(email) > 120:
        return False
    
    # Basic email regex pattern
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_password(password: str) -> bool:
    """Validate password strength."""
    if not isinstance(password, str):
        return False
    
    # Basic validation: at least 8 characters
    if len(password) < 8 or len(password) > 255:
        return False
    
    # You can add more complex validation here
    # - At least one uppercase
    # - At least one lowercase  
    # - At least one number
    # - At least one special character
    
    return True


def validate_role(role: str) -> bool:
    """Validate user role against allowed roles."""
    if not isinstance(role, str):
        return False
    
    allowed_roles = ["admin", "lawyer", "judge", "citizen"]
    return role in allowed_roles


def validate_required_fields(data: Dict[str, Any], required_fields: List[str]) -> List[str]:
    """Check for missing required fields."""
    if not isinstance(data, dict):
        return required_fields.copy()
    
    missing = []
    for field in required_fields:
        if not data.get(field):
            missing.append(field)
    return missing


def validate_string_length(value: str, min_length: int = 1, max_length: int = 255) -> bool:
    """Validate string length constraints."""
    if not isinstance(value, str):
        return False
    return min_length <= len(value) <= max_length


def validate_numeric(value: Any, min_val: int = None, max_val: int = None) -> bool:
    """Validate numeric values with optional bounds."""
    try:
        num = int(value)
        if min_val is not None and num < min_val:
            return False
        if max_val is not None and num > max_val:
            return False
        return True
    except (ValueError, TypeError):
        return False


def sanitize_string(value: str) -> str:
    """Sanitize string input for security."""
    if not isinstance(value, str):
        return ""
    
    # Basic sanitization
    value = value.strip()
    # Remove potentially dangerous characters
    value = re.sub(r'[<>"\']', '', value)
    # Remove excessive whitespace
    value = re.sub(r'\s+', ' ', value)
    return value


def validate_case_data(data: Dict[str, Any]) -> tuple[bool, str]:
    """Validate case creation/update data."""
    errors = []
    
    # Title validation
    title = data.get("title", "")
    if not title or len(title.strip()) == 0:
        errors.append("Title is required")
    elif len(title) > 200:
        errors.append("Title must be less than 200 characters")
    
    # Description validation
    description = data.get("description", "")
    if len(description) > 2000:
        errors.append("Description must be less than 2000 characters")
    
    # Status validation
    status = data.get("status")
    if status and status not in ["Pending", "In Progress", "Completed", "Closed"]:
        errors.append("Invalid status")
    
    return len(errors) == 0, "; ".join(errors) if errors else ""


def validate_pagination_params(page: int = 1, per_page: int = 20) -> tuple[bool, str]:
    """Validate pagination parameters."""
    errors = []
    
    if page < 1:
        errors.append("Page must be greater than 0")
    
    if per_page < 1 or per_page > 100:
        errors.append("Per page must be between 1 and 100")
    
    return len(errors) == 0, "; ".join(errors) if errors else ""


def sanitize_filename(filename: str) -> str:
    """Sanitize filename for security."""
    if not isinstance(filename, str):
        return ""
    
    # Remove path traversal attempts
    filename = filename.replace("..", "").replace("/", "").replace("\\", "")
    
    # Remove potentially dangerous characters
    filename = re.sub(r'[<>:"|?*]', '', filename)
    
    # Limit length
    return filename[:255]
