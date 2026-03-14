# Frontend Integration Guide

## 🚀 Production API Configuration

### **Base URL Structure**
```
https://<service-name>.onrender.com/api/v1
```

**Example**: `https://judicial-supreme-backend.onrender.com/api/v1`

### **Socket.IO WebSocket Endpoint**
```
wss://<service-name>.onrender.com/socket.io/
```

**Example**: `wss://judicial-supreme-backend.onrender.com/socket.io/`

---

## 📡 Flutter Integration Configuration

### **API Service Configuration**
```dart
class ApiService {
  // Update this to your Render service URL
  static const String baseUrl = 'https://judicial-supreme-backend.onrender.com/api/v1';
  static const String wsUrl = 'wss://judicial-supreme-backend.onrender.com/socket.io/';
  
  // HTTP client with timeout
  static final Dio _dio = Dio(BaseOptions(
    baseUrl: baseUrl,
    connectTimeout: const Duration(seconds: 30),
    receiveTimeout: const Duration(seconds: 30),
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    },
  ));
}
```

### **Socket.IO Service Configuration**
```dart
class SocketService {
  late Socket _socket;
  
  void connect(String token) {
    _socket = io.io(
      ApiService.wsUrl,
      OptionBuilder()
          .setTransports(['websocket'])
          .setAuth({'token': token})  // JWT token for authentication
          .build(),
    );
    
    _socket.connect();
    
    // Event listeners
    _socket.on('connect', (_) => print('Connected to chat server'));
    _socket.on('chat_message', (data) => _handleChatMessage(data));
    _socket.on('typing', (data) => _handleTypingIndicator(data));
    _socket.on('notification', (data) => _handleNotification(data));
  }
  
  void sendMessage(String room, String message) {
    _socket.emit('chat_message', {
      'room': room,
      'message': message,
    });
  }
  
  void joinRoom(String room) {
    _socket.emit('join_room', {'room': room});
  }
  
  void sendTypingIndicator(String room, bool isTyping) {
    _socket.emit('typing', {
      'room': room,
      'typing': isTyping,
    });
  }
}
```

---

## 🔐 Authentication Flow

### **Login & Token Management**
```dart
class AuthService {
  Future<AuthResponse> login(String email, String password) async {
    try {
      final response = await ApiService._dio.post('/auth/login', data: {
        'email': email,
        'password': password,
      });
      
      if (response.data['success']) {
        final data = response.data['data'];
        return AuthResponse(
          accessToken: data['access_token'],
          refreshToken: data['refresh_token'],
          user: User.fromJson(data['user']),
        );
      } else {
        throw Exception(response.data['message']);
      }
    } catch (e) {
      throw Exception('Login failed: $e');
    }
  }
  
  Future<String> refreshToken(String refreshToken) async {
    try {
      final response = await ApiService._dio.post('/auth/refresh', data: {
        'refresh_token': refreshToken,
      });
      
      return response.data['data']['access_token'];
    } catch (e) {
      throw Exception('Token refresh failed: $e');
    }
  }
}
```

---

## 📱 API Endpoints Integration

### **Authentication**
```dart
// Login
POST /api/v1/auth/login
{
  "email": "user@example.com",
  "password": "password123"
}

// Response
{
  "success": true,
  "data": {
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "user": {
      "id": 1,
      "email": "user@example.com",
      "role": "lawyer"
    }
  }
}
```

### **Case Management**
```dart
// Get cases with pagination
GET /api/v1/case?limit=20&offset=0
Authorization: Bearer <access_token>

// Response
{
  "success": true,
  "data": {
    "items": [
      {
        "id": 1,
        "title": "Contract Dispute",
        "description": "Breach of contract case",
        "status": "Active",
        "created_at": "2026-03-14T12:00:00Z",
        "created_by": 1,
        "assigned_judge_id": 2
      }
    ],
    "pagination": {
      "total": 100,
      "limit": 20,
      "offset": 0,
      "has_next": true,
      "has_prev": false
    }
  }
}

// Create case
POST /api/v1/case/create
Authorization: Bearer <access_token>
{
  "title": "New Case Title",
  "description": "Case description"
}
```

### **Document Upload**
```dart
// Upload document
POST /api/v1/document/upload
Authorization: Bearer <access_token>
Content-Type: multipart/form-data

// Form data:
// file: <binary file data>
// case_id: 123
```

### **Hearing Management**
```dart
// Schedule hearing
POST /api/v1/hearing/schedule
Authorization: Bearer <access_token>
{
  "case_id": 123,
  "hearing_date": "2026-04-15T10:00:00Z",
  "description": "Initial hearing"
}

// Get case hearings
GET /api/v1/hearing/123
Authorization: Bearer <access_token>
```

### **AI Services**
```dart
// Case summary
POST /api/v1/ai/case-summary
Authorization: Bearer <access_token>
{
  "case_data": "Case details text...",
  "language": "en"
}

// Voice search
POST /api/v1/ai/voice-search
Authorization: Bearer <access_token>
{
  "text": "Search query..."
}

// Response format for all AI endpoints
{
  "success": true,
  "data": {
    "summary": "AI-generated summary...",
    "confidence": 0.95,
    "processing_time": 1.2
  }
}
```

---

## 🔧 Error Handling

### **Standard Error Response**
```dart
class ApiError implements Exception {
  final String message;
  final int? statusCode;
  final String? errorType;
  
  ApiError(this.message, {this.statusCode, this.errorType});
  
  factory ApiError.fromResponse(Map<String, dynamic> response) {
    return ApiError(
      response['message'] ?? 'Unknown error',
      statusCode: response['status_code'],
      errorType: response['error'],
    );
  }
}

// Usage in API calls
try {
  final response = await ApiService._dio.get('/case');
  // Handle success
} on DioException catch (e) {
  if (e.response?.data != null) {
    final apiError = ApiError.fromResponse(e.response!.data);
    throw apiError;
  }
  throw ApiError('Network error: $e');
}
```

---

## 📡 Real-time Features

### **Chat Integration**
```dart
class ChatService {
  void handleChatMessage(Map<String, dynamic> data) {
    final message = ChatMessage(
      id: data['id'],
      userId: data['user_id'],
      message: data['message'],
      timestamp: DateTime.parse(data['timestamp']),
      type: data['type'],
    );
    
    // Update UI with new message
    _addMessageToChat(message);
  }
  
  void sendChatMessage(String room, String message) {
    _socket.emit('chat_message', {
      'room': room,
      'message': message,
    });
  }
  
  void sendTypingIndicator(String room, bool isTyping) {
    _socket.emit('typing', {
      'room': room,
      'typing': isTyping,
    });
  }
}
```

### **Notifications**
```dart
class NotificationService {
  void handleNotification(Map<String, dynamic> data) {
    final notification = AppNotification(
      id: data['id'],
      title: data['title'],
      message: data['message'],
      type: data['type'],
      timestamp: DateTime.parse(data['timestamp']),
    );
    
    // Show local notification
    _showLocalNotification(notification);
    
    // Update UI notification list
    _addNotificationToList(notification);
  }
}
```

---

## 🔄 Token Refresh Strategy

### **Automatic Token Refresh**
```dart
class AuthInterceptor extends Interceptor {
  @override
  void onRequest(RequestOptions options, RequestInterceptorHandler handler) {
    // Add auth token to all requests
    final token = StorageService.getAccessToken();
    if (token != null) {
      options.headers['Authorization'] = 'Bearer $token';
    }
    handler.next(options);
  }
  
  @override
  void onError(DioException err, ErrorInterceptorHandler handler) {
    if (err.response?.statusCode == 401) {
      // Token expired, try to refresh
      _refreshTokenAndRetry(err, handler);
    } else {
      handler.next(err);
    }
  }
  
  Future<void> _refreshTokenAndRetry(
    DioException err,
    ErrorInterceptorHandler handler,
  ) async {
    try {
      final refreshToken = StorageService.getRefreshToken();
      if (refreshToken != null) {
        final newToken = await AuthService.refreshToken(refreshToken);
        StorageService.saveAccessToken(newToken);
        
        // Retry original request with new token
        final originalRequest = err.requestOptions;
        originalRequest.headers['Authorization'] = 'Bearer $newToken';
        
        final response = await ApiService._dio.fetch(originalRequest);
        handler.resolve(response);
        return;
      }
    } catch (e) {
      // Refresh failed, redirect to login
      NavigationService.navigateToLogin();
    }
    
    handler.next(err);
  }
}
```

---

## 📱 Testing Integration

### **Integration Test Checklist**
- [ ] Authentication flow works (login → token → refresh)
- [ ] Case CRUD operations with pagination
- [ ] Document upload functionality
- [ ] Hearing scheduling and retrieval
- [ ] Real-time chat via Socket.IO
- [ ] AI analysis endpoints
- [ ] Push notifications
- [ ] Error handling and offline scenarios

### **Test Data**
```dart
// Test user credentials (create these in your database)
const testUser = {
  'email': 'test@judicial.com',
  'password': 'TestPassword123!',
  'role': 'lawyer'
};

// Test case data
const testCase = {
  'title': 'Test Integration Case',
  'description': 'This is a test case for integration testing'
};
```

---

## 🚀 Production Deployment Steps

1. **Update Base URLs** in your Flutter app:
   ```dart
   static const String baseUrl = 'https://your-service.onrender.com/api/v1';
   static const String wsUrl = 'wss://your-service.onrender.com/socket.io/';
   ```

2. **Configure HTTPS** - Render provides automatic SSL certificates

3. **Test Integration**:
   ```bash
   # Run smoke tests against your deployed service
   python scripts/smoke_test.py https://your-service.onrender.com
   ```

4. **Monitor Performance**:
   - Check API response times
   - Monitor WebSocket connections
   - Verify rate limiting is working

5. **Deploy to App Stores** with production API URLs

---

## 📞 Support

For integration issues:
1. Check the [API Documentation](https://your-service.onrender.com/api/v1/docs/)
2. Review the [smoke test results](scripts/smoke_test.py)
3. Check structured logs in Render dashboard
4. Verify environment variables are correctly set
