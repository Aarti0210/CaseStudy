"""
Lazy initialization utilities for cold start optimization on Render Free tier.
"""

import os
from functools import lru_cache
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

# Global variables to track initialization state
_ai_service_initialized = False
_heavy_queries_cached = {}
_socketio_initialized = False


class LazyAIService:
    """Lazy initialization wrapper for AI services."""
    
    def __init__(self):
        self._service = None
        self._initialized = False
    
    def get_service(self):
        if not self._initialized:
            logger.info("Initializing AI service...")
            try:
                from app.ai.ai_service import AIService
                self._service = AIService()
                self._initialized = True
                logger.info("AI service initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize AI service: {e}")
                raise
        return self._service
    
    def is_initialized(self) -> bool:
        return self._initialized


class LazyDatabaseCache:
    """Lazy caching for expensive database queries."""
    
    @staticmethod
    @lru_cache(maxsize=128)
    def get_user_roles() -> Dict[int, str]:
        """Cache user roles to reduce database queries."""
        from app.models.user import User
        try:
            users = User.query.with_entities(User.id, User.role).all()
            return {user_id: role for user_id, role in users}
        except Exception as e:
            logger.error(f"Error caching user roles: {e}")
            return {}
    
    @staticmethod
    @lru_cache(maxsize=32)
    def get_case_statistics() -> Dict[str, Any]:
        """Cache case statistics for dashboard."""
        from app.models.case import Case
        try:
            total_cases = Case.query.count()
            pending_cases = Case.query.filter_by(status='Pending').count()
            active_cases = Case.query.filter_by(status='Active').count()
            
            return {
                'total_cases': total_cases,
                'pending_cases': pending_cases,
                'active_cases': active_cases,
                'cached_at': str(__import__('datetime').datetime.utcnow())
            }
        except Exception as e:
            logger.error(f"Error caching case statistics: {e}")
            return {}
    
    @staticmethod
    def clear_cache():
        """Clear all cached data."""
        LazyDatabaseCache.get_user_roles.cache_clear()
        LazyDatabaseCache.get_case_statistics.cache_clear()
        logger.info("Database cache cleared")


class LazySocketIO:
    """Lazy initialization for SocketIO connections."""
    
    def __init__(self):
        self._initialized = False
        self._connected_clients = set()
    
    def initialize_if_needed(self, socketio_instance):
        if not self._initialized:
            logger.info("Initializing SocketIO handlers...")
            try:
                # Register SocketIO event handlers here
                self._register_handlers(socketio_instance)
                self._initialized = True
                logger.info("SocketIO handlers initialized")
            except Exception as e:
                logger.error(f"Failed to initialize SocketIO: {e}")
                raise
    
    def _register_handlers(self, socketio_instance):
        """Register SocketIO event handlers."""
        from flask_socketio import emit
        
        @socketio_instance.on('connect')
        def handle_connect():
            self._connected_clients.add(id(socketio_instance))
            logger.info(f"Client connected. Total clients: {len(self._connected_clients)}")
        
        @socketio_instance.on('disconnect')
        def handle_disconnect():
            self._connected_clients.discard(id(socketio_instance))
            logger.info(f"Client disconnected. Total clients: {len(self._connected_clients)}")
    
    def is_initialized(self) -> bool:
        return self._initialized


# Global instances
lazy_ai_service = LazyAIService()
lazy_db_cache = LazyDatabaseCache()
lazy_socketio = LazySocketIO()


def get_ai_service():
    """Get AI service instance, initializing if necessary."""
    return lazy_ai_service.get_service()


def get_cached_user_roles():
    """Get cached user roles."""
    return lazy_db_cache.get_user_roles()


def get_cached_case_stats():
    """Get cached case statistics."""
    return lazy_db_cache.get_case_statistics()


def initialize_socketio_if_needed(socketio_instance):
    """Initialize SocketIO if not already done."""
    lazy_socketio.initialize_if_needed(socketio_instance)


def is_cold_start_environment() -> bool:
    """Check if we're in a cold start environment like Render Free."""
    # Check for Render-specific environment variables
    is_render = os.getenv('RENDER', '') == 'true'
    is_free_tier = os.getenv('RENDER_SERVICE_TYPE', '') == 'free'
    
    # Also check for other indicators of cold start environments
    memory_limit = os.getenv('MEMORY_LIMIT', '')
    low_memory = '256Mi' in memory_limit or '512Mi' in memory_limit
    
    return is_render and (is_free_tier or low_memory)


# Export aliases for easier importing
LazyAI = LazyAIService
LazyDB = LazyDatabaseCache
LazySocket = LazySocketIO
