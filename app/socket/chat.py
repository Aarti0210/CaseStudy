from flask_socketio import emit, join_room, leave_room, disconnect
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from app.middleware.structured_logging import structured_logger


def register_socket(socketio):
    """Register Socket.IO event handlers with authentication and logging."""

    @socketio.on("connect")
    def handle_connect():
        """Handle client connection with JWT authentication."""
        try:
            # Verify JWT token for Socket.IO connection
            verify_jwt_in_request()
            identity = get_jwt_identity()
            
            structured_logger.log_auth_event(
                'websocket_connect',
                user_id=identity.get('id') if identity else None,
                details={'socket_id': id(socketio)}
            )
            
            emit('connected', {
                'status': 'connected',
                'user_id': identity.get('id') if identity else None,
                'message': 'Successfully connected to chat server'
            })
            
        except Exception as e:
            structured_logger.log_auth_event(
                'websocket_connect_failed',
                details={'error': str(e)}
            )
            # Reject connection if authentication fails
            return False

    @socketio.on("disconnect")
    def handle_disconnect():
        """Handle client disconnection."""
        try:
            verify_jwt_in_request()
            identity = get_jwt_identity()
            
            structured_logger.log_auth_event(
                'websocket_disconnect',
                user_id=identity.get('id') if identity else None,
                details={'socket_id': id(socketio)}
            )
        except:
            pass  # Allow graceful disconnection even without valid token

    @socketio.on("join_room")
    def handle_join_room(data):
        """Handle joining a chat room."""
        try:
            verify_jwt_in_request()
            identity = get_jwt_identity()
            
            room = data.get('room')
            if not room:
                emit('error', {'message': 'Room name is required'})
                return
            
            join_room(room)
            
            structured_logger.log_case_action(
                'joined_chat_room',
                case_id=room if room.isdigit() else None,
                user_id=identity.get('id'),
                details={'room': room}
            )
            
            emit('room_joined', {
                'room': room,
                'user_id': identity.get('id'),
                'message': f'User {identity.get("id")} joined room {room}'
            }, room=room, include_self=False)
            
        except Exception as e:
            emit('error', {'message': 'Authentication required to join room'})

    @socketio.on("leave_room")
    def handle_leave_room(data):
        """Handle leaving a chat room."""
        try:
            verify_jwt_in_request()
            identity = get_jwt_identity()
            
            room = data.get('room')
            if not room:
                emit('error', {'message': 'Room name is required'})
                return
            
            leave_room(room)
            
            structured_logger.log_case_action(
                'left_chat_room',
                case_id=room if room.isdigit() else None,
                user_id=identity.get('id'),
                details={'room': room}
            )
            
            emit('room_left', {
                'room': room,
                'user_id': identity.get('id'),
                'message': f'User {identity.get("id")} left room {room}'
            }, room=room, include_self=False)
            
        except Exception as e:
            emit('error', {'message': 'Authentication required'})

    @socketio.on("chat_message")
    def handle_chat_message(data):
        """Handle chat messages in a room."""
        try:
            verify_jwt_in_request()
            identity = get_jwt_identity()
            
            room = data.get('room')
            message = data.get('message')
            
            if not room or not message:
                emit('error', {'message': 'Room and message are required'})
                return
            
            # Log the message
            structured_logger.log_case_action(
                'chat_message_sent',
                case_id=room if room.isdigit() else None,
                user_id=identity.get('id'),
                details={
                    'room': room,
                    'message_length': len(message),
                    'message_preview': message[:50] + '...' if len(message) > 50 else message
                }
            )
            
            # Broadcast message to room
            emit('chat_message', {
                'id': f"{identity.get('id')}_{hash(message)}_{id(socketio)}",
                'room': room,
                'user_id': identity.get('id'),
                'message': message,
                'timestamp': str(__import__('datetime').datetime.utcnow().isoformat() + 'Z'),
                'type': 'message'
            }, room=room)
            
        except Exception as e:
            emit('error', {'message': 'Authentication required to send messages'})

    @socketio.on("typing")
    def handle_typing(data):
        """Handle typing indicators."""
        try:
            verify_jwt_in_request()
            identity = get_jwt_identity()
            
            room = data.get('room')
            is_typing = data.get('typing', False)
            
            if not room:
                return
            
            # Broadcast typing indicator (excluding sender)
            emit('typing', {
                'room': room,
                'user_id': identity.get('id'),
                'typing': is_typing,
                'type': 'typing_indicator'
            }, room=room, include_self=False)
            
        except Exception:
            # Silently fail for typing indicators
            pass

    @socketio.on("notification")
    def handle_notification(data):
        """Handle notification events."""
        try:
            verify_jwt_in_request()
            identity = get_jwt_identity()
            
            # Only admins and judges can send system notifications
            if identity.get('role') not in ['admin', 'judge']:
                emit('error', {'message': 'Insufficient permissions'})
                return
            
            notification_data = {
                'id': f"notif_{identity.get('id')}_{id(socketio)}",
                'user_id': identity.get('id'),
                'title': data.get('title', 'System Notification'),
                'message': data.get('message', ''),
                'type': data.get('type', 'info'),
                'timestamp': str(__import__('datetime').datetime.utcnow().isoformat() + 'Z')
            }
            
            # Broadcast to all connected clients or specific room
            target_room = data.get('room', 'global')
            emit('notification', notification_data, room=target_room)
            
            structured_logger.log_system_event(
                'notification_broadcast',
                f'Notification sent to {target_room}',
                'info',
                {
                    'sender_id': identity.get('id'),
                    'room': target_room,
                    'notification_type': data.get('type', 'info')
                }
            )
            
        except Exception as e:
            emit('error', {'message': 'Failed to send notification'})

    # Legacy compatibility endpoints
    @socketio.on("join")
    def handle_join_legacy(data):
        """Legacy join endpoint - redirects to join_room."""
        handle_join_room(data)

    @socketio.on("message")
    def handle_message_legacy(data):
        """Legacy message endpoint - redirects to chat_message."""
        handle_chat_message(data)
