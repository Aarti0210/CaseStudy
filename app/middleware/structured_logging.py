"""
Structured logging middleware for API requests, authentication, case actions, and AI usage.
"""

import json
import logging
import time
import uuid
from datetime import datetime
from typing import Dict, Any, Optional
from flask import Flask, request, g
from flask_jwt_extended import get_jwt_identity


class StructuredLogger:
    """Structured logger with consistent formatting."""
    
    def __init__(self, app: Optional[Flask] = None):
        self.app = app
        self.logger = logging.getLogger('judicial_backend')
        if app:
            self.init_app(app)
    
    def init_app(self, app: Flask):
        """Initialize the logger with Flask app."""
        self.app = app
        self.logger = logging.getLogger('judicial_backend')
        
        # Set up request logging middleware
        app.before_request(self._before_request)
        app.after_request(self._after_request)
        app.teardown_appcontext(self._teardown_request)
    
    def _before_request(self):
        """Store request start time and generate request ID."""
        g.start_time = time.time()
        g.request_id = request.headers.get('X-Request-ID') or str(uuid.uuid4())
        g.request_data = {
            'method': request.method,
            'url': request.url,
            'path': request.path,
            'user_agent': request.headers.get('User-Agent', ''),
            'remote_addr': request.remote_addr,
            'content_length': request.content_length
        }
    
    def _after_request(self, response):
        """Log request completion."""
        if hasattr(g, 'start_time'):
            duration = time.time() - g.start_time
            
            log_data = {
                'event_type': 'api_request',
                'request_id': getattr(g, 'request_id', 'unknown'),
                'method': request.method,
                'path': request.path,
                'status_code': response.status_code,
                'duration_ms': round(duration * 1000, 2),
                'response_size': len(response.get_data()) if hasattr(response, 'get_data') else 0,
                'timestamp': datetime.utcnow().isoformat(),
                'user_id': self._get_user_id(),
                'remote_addr': request.remote_addr
            }
            
            # Log at different levels based on status code
            if response.status_code >= 500:
                self.logger.error(json.dumps(log_data))
            elif response.status_code >= 400:
                self.logger.warning(json.dumps(log_data))
            else:
                self.logger.info(json.dumps(log_data))
        
        return response
    
    def _teardown_request(self, exception):
        """Log request exceptions."""
        if exception:
            log_data = {
                'event_type': 'request_error',
                'request_id': getattr(g, 'request_id', 'unknown'),
                'method': request.method,
                'path': request.path,
                'error_type': type(exception).__name__,
                'error_message': str(exception),
                'timestamp': datetime.utcnow().isoformat(),
                'user_id': self._get_user_id(),
                'remote_addr': request.remote_addr
            }
            self.logger.error(json.dumps(log_data))
    
    def _get_user_id(self) -> Optional[str]:
        """Get current user ID from JWT token."""
        try:
            identity = get_jwt_identity()
            return identity.get('id') if identity else None
        except Exception:
            return None
    
    def log_auth_event(self, event_type: str, user_id: Optional[str] = None, 
                      details: Optional[Dict[str, Any]] = None):
        """Log authentication events."""
        log_data = {
            'event_type': 'auth_event',
            'auth_event': event_type,
            'user_id': user_id or self._get_user_id(),
            'timestamp': datetime.utcnow().isoformat(),
            'remote_addr': request.remote_addr if request else None,
            'user_agent': request.headers.get('User-Agent') if request else None,
            'request_id': getattr(g, 'request_id', 'unknown')
        }
        
        if details:
            log_data.update(details)
        
        level = logging.INFO if event_type in ['login_success', 'logout'] else logging.WARNING
        self.logger.log(level, json.dumps(log_data))
    
    def log_case_action(self, action: str, case_id: int, user_id: Optional[str] = None,
                        details: Optional[Dict[str, Any]] = None):
        """Log case-related actions."""
        log_data = {
            'event_type': 'case_action',
            'action': action,
            'case_id': case_id,
            'user_id': user_id or self._get_user_id(),
            'timestamp': datetime.utcnow().isoformat(),
            'request_id': getattr(g, 'request_id', 'unknown')
        }
        
        if details:
            log_data.update(details)
        
        self.logger.info(json.dumps(log_data))
    
    def log_ai_usage(self, model: str, tokens_used: int, response_time_ms: float,
                     user_id: Optional[str] = None, case_id: Optional[int] = None,
                     details: Optional[Dict[str, Any]] = None):
        """Log AI service usage."""
        log_data = {
            'event_type': 'ai_usage',
            'model': model,
            'tokens_used': tokens_used,
            'response_time_ms': round(response_time_ms, 2),
            'user_id': user_id or self._get_user_id(),
            'case_id': case_id,
            'timestamp': datetime.utcnow().isoformat(),
            'request_id': getattr(g, 'request_id', 'unknown')
        }
        
        if details:
            log_data.update(details)
        
        self.logger.info(json.dumps(log_data))
    
    def log_system_event(self, event_type: str, message: str, level: str = 'info',
                        details: Optional[Dict[str, Any]] = None):
        """Log system-level events."""
        log_data = {
            'event_type': 'system_event',
            'system_event': event_type,
            'message': message,
            'timestamp': datetime.utcnow().isoformat(),
            'service': 'judicial-backend'
        }
        
        if details:
            log_data.update(details)
        
        log_level = getattr(logging, level.upper(), logging.INFO)
        self.logger.log(log_level, json.dumps(log_data))


# Global instance
structured_logger = StructuredLogger()


def init_structured_logging(app: Flask):
    """Initialize structured logging for the Flask app."""
    structured_logger.init_app(app)
    
    # Log application startup
    structured_logger.log_system_event(
        'application_startup',
        'Judicial backend application started',
        'info',
        {
            'environment': app.config.get('FLASK_ENV', 'unknown'),
            'debug_mode': app.config.get('DEBUG', False)
        }
    )
