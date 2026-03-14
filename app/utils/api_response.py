from typing import Any, Dict, Optional, Tuple

from flask import jsonify


def api_response(
    success: bool,
    data: Optional[Dict[str, Any]] = None,
    message: Optional[str] = None,
    status_code: int = 200,
) -> Tuple[Any, int]:
    """Standard API response wrapper.

    Shape expected by Flutter client:
        {
            "success": true/false,
            "data": {...} | null,
            "message": "optional human‑readable string"
        }
    """

    payload: Dict[str, Any] = {
        "success": success,
        "data": data if data is not None else None,
    }
    if message is not None:
        payload["message"] = message

    return jsonify(payload), status_code


def success_response(
    data: Optional[Dict[str, Any]] = None,
    message: Optional[str] = None,
    status_code: int = 200,
) -> Tuple[Any, int]:
    return api_response(True, data=data, message=message, status_code=status_code)


def error_response(
    message: str,
    status_code: int = 400,
    data: Optional[Dict[str, Any]] = None,
) -> Tuple[Any, int]:
    return api_response(False, data=data, message=message, status_code=status_code)

