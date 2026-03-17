# Complete Flutter Integration Guide

## 🚀 Production API Configuration

### **Base URLs**
```dart
// Production URLs (after Render deployment)
static const String baseUrl = 'https://judicial-supreme-backend.onrender.com/api/v1';
static const String wsUrl = 'wss://judicial-supreme-backend.onrender.com/socket.io/';

// Local development (if needed)
static const String localBaseUrl = 'http://127.0.0.1:8000/api/v1';
static const String localWsUrl = 'ws://127.0.0.1:8000/socket.io/';
```

---

## 🔐 Authentication System

### **Login Flow**
```dart
// POST /api/v1/auth/login
{
  "email": "user@example.com",
  "password": "password123"
}

// Success Response
{
  "success": true,
  "data": {
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "user": {
      "id": 1,
      "email": "user@example.com",
      "role": "lawyer",
      "name": "John Doe",
      "created_at": "2026-03-14T12:00:00Z"
    }
  }
}
```

### **Token Management**
```dart
class AuthManager {
  static const Duration accessTokenExpiry = Duration(hours: 1);
  static const Duration refreshTokenExpiry = Duration(hours: 24);
  
  // Store tokens securely
  static Future<void> saveTokens(String accessToken, String refreshToken) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('access_token', accessToken);
    await prefs.setString('refresh_token', refreshToken);
  }
  
  // Auto-refresh token
  static Future<String> refreshToken(String refreshToken) async {
    final response = await http.post(
      Uri.parse('$baseUrl/auth/refresh'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'refresh_token': refreshToken}),
    );
    
    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      return data['data']['access_token'];
    } else {
      throw Exception('Token refresh failed');
    }
  }
}
```

---

## 📱 API Endpoints Complete Reference

### **1. Authentication Endpoints**

#### **Login**
```dart
POST /api/v1/auth/login
Headers: Content-Type: application/json
Body: { "email": "string", "password": "string" }
Rate Limit: 20 per hour
```

#### **Register**
```dart
POST /api/v1/auth/signup
Headers: Content-Type: application/json
Body: { 
  "email": "string", 
  "password": "string",
  "name": "string",
  "role": "citizen|lawyer|judge|admin"
}
Rate Limit: 10 per hour
```

#### **Refresh Token**
```dart
POST /api/v1/auth/refresh
Headers: Content-Type: application/json
Body: { "refresh_token": "string" }
```

#### **OTP Verification**
```dart
POST /api/v1/auth/otp/request
Body: { "email": "string" }

POST /api/v1/auth/otp/verify
Body: { "email": "string", "otp": "string" }
```

---

### **2. Case Management**

#### **Get Cases (Paginated)**
```dart
GET /api/v1/case?limit=20&offset=0
Headers: Authorization: Bearer <token>
Response: {
  "success": true,
  "data": {
    "items": [
      {
        "id": 1,
        "title": "Contract Dispute",
        "description": "Breach of contract case",
        "status": "Pending|Active|Closed|On Hold",
        "created_at": "2026-03-14T12:00:00Z",
        "created_by": 1,
        "assigned_judge_id": 2,
        "case_number": "CASE-2026-001"
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
```

#### **Create Case**
```dart
POST /api/v1/case/create
Headers: Authorization: Bearer <token>
Body: {
  "title": "string",
  "description": "string",
  "client_name": "string (optional)",
  "case_type": "string (optional)"
}
```

#### **Update Case**
```dart
PUT /api/v1/case/{case_id}
Headers: Authorization: Bearer <token>
Body: {
  "title": "string",
  "description": "string",
  "status": "Pending|Active|Closed|On Hold"
}
```

#### **Assign Judge**
```dart
POST /api/v1/case/{case_id}/assign-judge
Headers: Authorization: Bearer <token>
Body: { "judge_id": 2 }
Roles: admin
```

---

### **3. Document Management**

#### **Upload Document**
```dart
POST /api/v1/document/upload
Headers: 
  - Authorization: Bearer <token>
  - Content-Type: multipart/form-data
Body: FormData
  - file: <binary file data>
  - case_id: 123
  - title: "Document Title" (optional)
  - description: "Document Description" (optional)

Allowed file types: PDF, DOC, DOCX, JPG, JPEG, PNG
Max file size: 16MB
```

#### **Get Case Documents**
```dart
GET /api/v1/document/{case_id}?limit=20&offset=0
Headers: Authorization: Bearer <token>
Response: {
  "success": true,
  "data": {
    "items": [
      {
        "id": 1,
        "case_id": 123,
        "title": "Contract Agreement",
        "filename": "contract.pdf",
        "file_path": "/uploads/contract.pdf",
        "uploaded_by": 1,
        "uploaded_at": "2026-03-14T12:00:00Z",
        "file_size": 1024000
      }
    ],
    "pagination": {...}
  }
}
```

#### **Delete Document**
```dart
DELETE /api/v1/document/{document_id}
Headers: Authorization: Bearer <token>
Roles: lawyer, admin
```

---

### **4. Hearing Management**

#### **Schedule Hearing**
```dart
POST /api/v1/hearing/schedule
Headers: Authorization: Bearer <token>
Body: {
  "case_id": 123,
  "hearing_date": "2026-04-15T10:00:00Z",
  "description": "Initial hearing",
  "location": "Court Room 1",
  "type": "initial|follow_up|final"
}
Roles: judge
```

#### **Get Case Hearings**
```dart
GET /api/v1/hearing/{case_id}
Headers: Authorization: Bearer <token>
Response: {
  "success": true,
  "data": [
    {
      "id": 1,
      "case_id": 123,
      "hearing_date": "2026-04-15T10:00:00Z",
      "description": "Initial hearing",
      "status": "Scheduled|Completed|Cancelled",
      "judge_id": 2,
      "location": "Court Room 1"
    }
  ]
}
```

#### **Update Hearing**
```dart
PUT /api/v1/hearing/{hearing_id}
Headers: Authorization: Bearer <token>
Body: {
  "hearing_date": "2026-04-15T10:00:00Z",
  "status": "Scheduled|Completed|Cancelled"
}
Roles: judge
```

---

### **5. Notifications**

#### **Get User Notifications**
```dart
GET /api/v1/notification/user/{user_id}?limit=20&offset=0
Headers: Authorization: Bearer <token>
Response: {
  "success": true,
  "data": {
    "items": [
      {
        "id": 1,
        "user_id": 1,
        "title": "New Case Assigned",
        "message": "You have been assigned to case #123",
        "type": "case_assignment|hearing_reminder|system_update",
        "read": false,
        "created_at": "2026-03-14T12:00:00Z"
      }
    ],
    "pagination": {...}
  }
}
```

#### **Mark as Read**
```dart
PUT /api/v1/notification/{notification_id}/read
Headers: Authorization: Bearer <token>
```

#### **Send Notification**
```dart
POST /api/v1/notification/send
Headers: Authorization: Bearer <token>
Body: {
  "user_id": 1,
  "title": "string",
  "message": "string",
  "type": "case_assignment|hearing_reminder|system_update"
}
Roles: admin, judge, lawyer
```

---

### **6. AI Services**

#### **Case Summary**
```dart
POST /api/v1/ai/case-summary
Headers: Authorization: Bearer <token>
Body: {
  "case_data": "Case details text...",
  "language": "en|hi|es|fr" (optional, default: en)
}
Rate Limit: 30 per hour
Response: {
  "success": true,
  "data": {
    "summary": "AI-generated case summary...",
    "key_points": ["Point 1", "Point 2"],
    "confidence": 0.95,
    "processing_time": 1.2
  }
}
```

#### **Voice Search**
```dart
POST /api/v1/ai/voice-search
Headers: Authorization: Bearer <token>
Body: {
  "text": "Search query from voice input",
  "language": "en|hi|es|fr" (optional)
}
Rate Limit: 60 per hour
```

#### **Explain Order**
```dart
POST /api/v1/ai/explain-order
Headers: Authorization: Bearer <token>
Body: {
  "text": "Legal order text...",
  "language": "en|hi|es|fr" (optional)
}
Rate Limit: 20 per hour
```

#### **Draft Notice**
```dart
POST /api/v1/ai/draft-notice
Headers: Authorization: Bearer <token>
Body: {
  "client_name": "John Doe",
  "case_type": "contract_dispute",
  "facts": "Case facts...",
  "language": "en|hi|es|fr" (optional)
}
Roles: lawyer
Rate Limit: 30 per hour
```

#### **Evidence Summary**
```dart
POST /api/v1/ai/evidence-summary
Headers: Authorization: Bearer <token>
Body: {
  "text": "Evidence text...",
  "language": "en|hi|es|fr" (optional)
}
Roles: lawyer
Rate Limit: 40 per hour
```

#### **Strategy Suggestion**
```dart
POST /api/v1/ai/strategy-suggestion
Headers: Authorization: Bearer <token>
Body: {
  "case_summary": "Case summary...",
  "opponent_claims": "Opponent claims...",
  "language": "en|hi|es|fr" (optional)
}
Roles: lawyer
Rate Limit: 20 per hour
```

#### **Predict Delay**
```dart
POST /api/v1/ai/predict-delay
Headers: Authorization: Bearer <token>
Body: {
  "case_data": "Case details...",
  "language": "en|hi|es|fr" (optional)
}
Roles: lawyer, judge, admin
Rate Limit: 10 per minute
```

---

### **7. Payment Processing**

#### **Create Payment**
```dart
POST /api/v1/payment/create
Headers: Authorization: Bearer <token>
Body: {
  "case_id": 123,
  "amount": 1000.00,
  "payment_method": "credit_card|debit_card|upi|net_banking",
  "description": "Legal consultation fee"
}
```

#### **Get Payment**
```dart
GET /api/v1/payment/{payment_id}
Headers: Authorization: Bearer <token>
```

#### **Get Case Payments**
```dart
GET /api/v1/payment/case/{case_id}
Headers: Authorization: Bearer <token>
```

---

### **8. Audit Logs (Admin Only)**

#### **Get System Logs**
```dart
GET /api/v1/audit/logs?limit=20&offset=0
Headers: Authorization: Bearer <token>
Roles: admin
Response: {
  "success": true,
  "data": {
    "items": [
      {
        "id": 1,
        "user_id": 1,
        "action": "case_created",
        "resource_type": "case",
        "resource_id": 123,
        "details": {"case_title": "Contract Dispute"},
        "ip_address": "192.168.1.1",
        "timestamp": "2026-03-14T12:00:00Z"
      }
    ],
    "pagination": {...}
  }
}
```

---

## 📡 Real-time WebSocket Events

### **Connection Setup**
```dart
import 'package:socket_io_client/socket_io_client.dart' as IO;

class SocketService {
  late IO.Socket _socket;
  
  void connect(String token) {
    _socket = IO.io(wsUrl, IO.OptionBuilder()
        .setTransports(['websocket'])
        .setAuth({'token': token})
        .build());
    
    _socket.connect();
    
    // Event listeners
    _socket.on('connect', (_) => print('Connected to chat server'));
    _socket.on('disconnect', (_) => print('Disconnected from chat server'));
    _socket.on('error', (error) => print('Socket error: $error'));
    
    // Chat events
    _socket.on('chat_message', (data) => _handleChatMessage(data));
    _socket.on('typing', (data) => _handleTypingIndicator(data));
    _socket.on('notification', (data) => _handleNotification(data));
    
    // Room events
    _socket.on('room_joined', (data) => _handleRoomJoined(data));
    _socket.on('room_left', (data) => _handleRoomLeft(data));
  }
  
  void disconnect() {
    _socket.disconnect();
  }
}
```

### **Chat Events**

#### **Join Room**
```dart
socket.emit('join_room', {
  'room': '123', // case_id as room
});
```

#### **Send Message**
```dart
socket.emit('chat_message', {
  'room': '123',
  'message': 'Hello, I have a question about the case.',
});
```

#### **Typing Indicator**
```dart
socket.emit('typing', {
  'room': '123',
  'typing': true, // or false when stopped typing
});
```

#### **Leave Room**
```dart
socket.emit('leave_room', {
  'room': '123',
});
```

### **Event Handlers**
```dart
void _handleChatMessage(Map<String, dynamic> data) {
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

void _handleTypingIndicator(Map<String, dynamic> data) {
  final userId = data['user_id'];
  final isTyping = data['typing'];
  
  // Update typing indicator in UI
  _updateTypingIndicator(userId, isTyping);
}

void _handleNotification(Map<String, dynamic> data) {
  final notification = AppNotification(
    id: data['id'],
    title: data['title'],
    message: data['message'],
    type: data['type'],
    timestamp: DateTime.parse(data['timestamp']),
  );
  
  // Show notification
  _showNotification(notification);
}
```

---

## 🔧 HTTP Client Configuration

### **Dio Setup with Interceptors**
```dart
import 'package:dio/dio.dart';

class ApiService {
  static final Dio _dio = Dio(BaseOptions(
    baseUrl: baseUrl,
    connectTimeout: const Duration(seconds: 30),
    receiveTimeout: const Duration(seconds: 30),
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    },
  ));
  
  static void initialize() {
    // Add auth interceptor
    _dio.interceptors.add(AuthInterceptor());
    
    // Add logging interceptor
    _dio.interceptors.add(LogInterceptor(
      requestBody: true,
      responseBody: true,
      logPrint: (obj) => print(obj),
    ));
    
    // Add error handling
    _dio.interceptors.add(ErrorInterceptor());
  }
  
  static Future<Response> get(String path, {Map<String, dynamic>? queryParameters}) =>
      _dio.get(path, queryParameters: queryParameters);
  
  static Future<Response> post(String path, {dynamic data}) =>
      _dio.post(path, data: data);
  
  static Future<Response> put(String path, {dynamic data}) =>
      _dio.put(path, data: data);
  
  static Future<Response> delete(String path) =>
      _dio.delete(path);
}
```

### **Auth Interceptor**
```dart
class AuthInterceptor extends Interceptor {
  @override
  void onRequest(RequestOptions options, RequestInterceptorHandler handler) async {
    // Add auth token
    final token = await StorageService.getAccessToken();
    if (token != null) {
      options.headers['Authorization'] = 'Bearer $token';
    }
    handler.next(options);
  }
  
  @override
  void onError(DioException err, ErrorInterceptorHandler handler) async {
    if (err.response?.statusCode == 401) {
      // Token expired, try to refresh
      try {
        final refreshToken = await StorageService.getRefreshToken();
        if (refreshToken != null) {
          final newToken = await AuthManager.refreshToken(refreshToken);
          await StorageService.saveAccessToken(newToken);
          
          // Retry original request
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
    }
    handler.next(err);
  }
}
```

---

## 📱 Data Models

### **User Model**
```dart
class User {
  final int id;
  final String email;
  final String name;
  final String role;
  final DateTime createdAt;
  
  User({
    required this.id,
    required this.email,
    required this.name,
    required this.role,
    required this.createdAt,
  });
  
  factory User.fromJson(Map<String, dynamic> json) => User(
    id: json['id'],
    email: json['email'],
    name: json['name'] ?? '',
    role: json['role'],
    createdAt: DateTime.parse(json['created_at']),
  );
}
```

### **Case Model**
```dart
class Case {
  final int id;
  final String title;
  final String description;
  final String status;
  final DateTime createdAt;
  final int createdBy;
  final int? assignedJudgeId;
  final String? caseNumber;
  
  Case({
    required this.id,
    required this.title,
    required this.description,
    required this.status,
    required this.createdAt,
    required this.createdBy,
    this.assignedJudgeId,
    this.caseNumber,
  });
  
  factory Case.fromJson(Map<String, dynamic> json) => Case(
    id: json['id'],
    title: json['title'],
    description: json['description'] ?? '',
    status: json['status'],
    createdAt: DateTime.parse(json['created_at']),
    createdBy: json['created_by'],
    assignedJudgeId: json['assigned_judge_id'],
    caseNumber: json['case_number'],
  );
}
```

### **Pagination Model**
```dart
class Pagination {
  final int total;
  final int limit;
  final int offset;
  final bool hasNext;
  final bool hasPrev;
  
  Pagination({
    required this.total,
    required this.limit,
    required this.offset,
    required this.hasNext,
    required this.hasPrev,
  });
  
  factory Pagination.fromJson(Map<String, dynamic> json) => Pagination(
    total: json['total'],
    limit: json['limit'],
    offset: json['offset'],
    hasNext: json['has_next'],
    hasPrev: json['has_prev'],
  );
}
```

---

## 🔄 Error Handling

### **API Error Model**
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
  
  @override
  String toString() => 'ApiError: $message';
}
```

### **Error Handling Service**
```dart
class ErrorService {
  static void handleError(dynamic error) {
    if (error is ApiError) {
      switch (error.statusCode) {
        case 401:
          // Unauthorized - redirect to login
          NavigationService.navigateToLogin();
          break;
        case 403:
          // Forbidden - show permission error
          _showErrorDialog('Permission Denied', 'You don\'t have permission to perform this action.');
          break;
        case 404:
          // Not found
          _showErrorDialog('Not Found', 'The requested resource was not found.');
          break;
        case 429:
          // Rate limit exceeded
          _showErrorDialog('Rate Limit', 'Too many requests. Please try again later.');
          break;
        case 500:
          // Server error
          _showErrorDialog('Server Error', 'Something went wrong. Please try again later.');
          break;
        default:
          _showErrorDialog('Error', error.message);
      }
    } else {
      _showErrorDialog('Error', 'An unexpected error occurred.');
    }
  }
  
  static void _showErrorDialog(String title, String message) {
    // Show error dialog using your preferred UI framework
    showDialog(
      context: navigatorKey.currentContext!,
      builder: (context) => AlertDialog(
        title: Text(title),
        content: Text(message),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('OK'),
          ),
        ],
      ),
    );
  }
}
```

---

## 🧪 Testing Integration

### **Test Configuration**
```dart
// For testing, you can use the local server
const String testBaseUrl = 'http://127.0.0.1:8000/api/v1';
const String testWsUrl = 'ws://127.0.0.1:8000/socket.io/';

// Test user credentials
const testUser = {
  'email': 'test@judicial.com',
  'password': 'TestPassword123!',
  'role': 'lawyer'
};
```

### **Integration Test Checklist**
- [ ] Authentication flow (login → token → refresh)
- [ ] Case CRUD operations with pagination
- [ ] Document upload functionality
- [ ] Hearing scheduling and retrieval
- [ ] Real-time chat via Socket.IO
- [ ] AI analysis endpoints
- [ ] Payment processing
- [ ] Push notifications
- [ ] Error handling and offline scenarios
- [ ] Rate limiting behavior

---

## 📊 Rate Limits

| Endpoint | Rate Limit | User Type |
|----------|------------|-----------|
| Login | 20 per hour | All |
| Signup | 10 per hour | All |
| Case Summary | 30 per hour | Citizen, Lawyer, Admin |
| Voice Search | 60 per hour | Citizen, Lawyer |
| Explain Order | 20 per hour | All |
| Draft Notice | 30 per hour | Lawyer |
| Evidence Summary | 40 per hour | Lawyer |
| Strategy Suggestion | 20 per hour | Lawyer |
| Predict Delay | 10 per minute | Lawyer, Judge, Admin |
| Default | 200 per day, 50 per hour | All |

---

## 🚀 Quick Start Checklist

### **1. Configuration**
```dart
// Update these constants in your Flutter app
static const String baseUrl = 'https://judicial-supreme-backend.onrender.com/api/v1';
static const String wsUrl = 'wss://judicial-supreme-backend.onrender.com/socket.io/';
```

### **2. Dependencies**
```yaml
dependencies:
  dio: ^5.4.0
  socket_io_client: ^2.0.3+1
  shared_preferences: ^2.2.2
  json_annotation: ^4.8.1
```

### **3. Initialization**
```dart
// In main.dart
void main() {
  ApiService.initialize();
  SocketService().connect(await StorageService.getAccessToken());
  runApp(MyApp());
}
```

### **4. First API Call**
```dart
// Test authentication
try {
  final response = await ApiService.post('/auth/login', data: {
    'email': 'test@example.com',
    'password': 'password123'
  });
  
  if (response.data['success']) {
    final tokens = response.data['data'];
    await StorageService.saveTokens(
      tokens['access_token'],
      tokens['refresh_token'],
    );
    print('Login successful!');
  }
} catch (e) {
  ErrorService.handleError(e);
}
```

---

## 📞 Support & Troubleshooting

### **Common Issues**
1. **CORS Errors**: Ensure backend is deployed and CORS is configured
2. **Socket Connection**: Use `wss://` for WebSocket connections in production
3. **Token Expiry**: Implement automatic token refresh
4. **Rate Limits**: Handle 429 responses gracefully
5. **File Uploads**: Use multipart/form-data for document uploads

### **Debug Tools**
- API Documentation: `https://your-service.onrender.com/api/v1/docs`
- Health Check: `https://your-service.onrender.com/health`
- Network Logs: Use Dio's logging interceptor
- Socket Debugging: Monitor socket events in browser console

---

**This complete integration guide provides everything needed for Flutter frontend integration with the Judicial Supreme Backend!** 🚀
