"""
Input validation utilities.
Centralizes validation logic for consistency and reusability.
"""

import re
from typing import Any, Dict, List


def validate_email(email: str) -> bool:
    """Validate email format."""
    if not isinstance(email, str):
        return False
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_password(password: str) -> bool:
    """Validate password strength."""
    if not isinstance(password, str):
        return False
    
    # Basic validation: at least 8 characters
    if len(password) < 8:
        return False
    
    # You can add more complex validation here
    # - At least one uppercase
    # - At least one lowercase
    # - At least one number
    # - At least one special character
    
    return True


def validate_required_fields(data: Dict[str, Any], required_fields: List[str]) -> List[str]:
    """Check for missing required fields."""
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


def validate_role(role: str) -> bool:
    """Validate user role."""
    allowed_roles = ["admin", "lawyer", "judge", "citizen"]
    return role in allowed_roles


def sanitize_string(value: str) -> str:
    """Sanitize string input."""
    if not isinstance(value, str):
        return ""
    
    # Basic sanitization
    value = value.strip()
    # Remove potentially dangerous characters
    value = re.sub(r'[<>"\']', '', value)
    return value
