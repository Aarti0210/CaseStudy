# Judicial Supreme Backend - Quick Start Guide

## Setup & Installation

### 1. Prerequisites
- Python 3.8+
- PostgreSQL or MySQL database (optional, SQLite for development)
- OpenAI API key (for AI features)

### 2. Clone & Install Dependencies
```bash
cd judicial_supreme_backend_v3
pip install -r requirements.txt
pip install pytest pytest-html  # for testing
```

### 3. Environment Configuration
```bash
cp .env.example .env
# Edit .env with your configuration
```

**Minimum Required Settings:**
```env
FLASK_ENV=development
SECRET_KEY=dev-secret-key-change-in-production
JWT_SECRET_KEY=jwt-secret-key
DB_HOST=localhost
DB_USER=root
DB_NAME=judicial
```

### 4. Database Setup (Development)
```bash
# Using SQLite (fastest for development)
export SQLALCHEMY_DATABASE_URI="sqlite:///judicial.db"
python run.py

# Or PostgreSQL/MySQL (ensure DATABASE_URL is set appropriately)
# Example: export DATABASE_URL=postgresql://user:pass@localhost:5432/judicial
python -c "from app import create_app; app = create_app(); app.app_context().push(); from app.extensions import db; db.create_all()"
```

### 5. Run the Application
```bash
# Development
python run.py

# Production
gunicorn wsgi:app -k eventlet -w 1 -b 0.0.0.0:8000
```

Server will be running at: **http://localhost:5000**

---

## API Usage Examples

### 1. User Registration
```bash
curl -X POST http://localhost:5000/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john@example.com",
    "password": "SecurePass@123",
    "role": "citizen"
  }'
```

### 2. User Login
```bash
curl -X POST http://localhost:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "password": "SecurePass@123"
  }'
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 1,
    "name": "John Doe",
    "email": "john@example.com",
    "role": "citizen"
  }
}
```

### 3. Create a Case
```bash
curl -X POST http://localhost:5000/case/create \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Johnson vs. Smith Property Dispute",
    "description": "Dispute over property boundary"
  }'
```

### 4. Get All Cases
```bash
curl -X GET http://localhost:5000/case \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 5. Schedule a Hearing
```bash
curl -X POST http://localhost:5000/hearing/schedule \
  -H "Authorization: Bearer JUDGE_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "case_id": 1,
    "hearing_date": "2026-03-20T10:00:00",
    "notes": "Initial hearing"
  }'
```

### 6. Upload a Document
```bash
curl -X POST http://localhost:5000/document/upload \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -F "case_id=1" \
  -F "file=@/path/to/document.pdf"
```

### 7. Use AI to Explain an Order
```bash
curl -X POST http://localhost:5000/ai/explain-order \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "The court hereby orders the defendant to pay...",
    "language": "en"
  }'
```

### 8. Get Case Summary (AI)
```bash
curl -X POST http://localhost:5000/ai/case-summary \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "case_data": "Full case details including parties, facts, issues...",
    "language": "en"
  }'
```

### 9. Predict Case Delay (ML)

The project includes a RandomForest model (version `v1`) for estimating expected case duration in days and classifying delay risk. The model is frozen for the DIPEX demo and returns deterministic predictions with a simple confidence heuristic.

Request:
```bash
curl -X POST http://localhost:5000/ai/predict-delay \
  -H "Authorization: Bearer YOUR_ADMIN_OR_JUDGE_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"case_data": {"case_type":"civil","number_of_hearings":3,"judge_workload":40,"document_count":5,"case_priority":"medium","filing_to_first_hearing_days":20,"court_level":"district","previous_adjournments":1}}'
```

Response contains `predicted_duration_days`, `risk_level` (Low/Moderate/High), `confidence`, and `model_version`.

Configuration:
- `LOW_DELAY_THRESHOLD` and `HIGH_DELAY_THRESHOLD` are configured via `app.config` or environment variables. Defaults: 365 and 900 days.

Model metadata:
```bash
curl -X GET http://localhost:5000/ai/model-info \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

Retraining (offline):
- To retrain the model use `python app/ml/train_model.py` (run offline). The training script saves `models/delay_model_v1.joblib` and updates `models/model_metadata.json`. Model v1 is frozen for demo; redeploying an updated model requires replacing the artifact and metadata and restarting the service.


### 9. Record a Payment
```bash
curl -X POST http://localhost:5000/payment/create \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "case_id": 1,
    "amount": 5000.00,
    "currency": "USD",
    "status": "pending"
  }'
```

### 10. Send Notification
```bash
curl -X POST http://localhost:5000/notification/send \
  -H "Authorization: Bearer ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 1,
    "message": "Your case hearing is scheduled for tomorrow"
  }'
```

---

## Testing

### Run All Tests
```bash
pytest tests/ -v
```

### Run Specific Test File
```bash
pytest tests/test_comprehensive.py -v
```

### Run Specific Test
```bash
pytest tests/test_comprehensive.py::test_create_case -v
```

### Generate Coverage Report
```bash
pytest tests/ --cov=app --cov-report=html
```

### Generate HTML Test Report
```bash
pytest tests/ -v --html=report.html --self-contained-html
```

---

## User Roles & Permissions

### Citizen
- ✅ Register/Login
- ✅ Create cases
- ✅ View own cases
- ✅ Upload documents
- ✅ View notifications
- ❌ Cannot manage other users' cases
- ❌ Cannot schedule hearings

### Lawyer
- ✅ All citizen privileges
- ✅ Create/update cases
- ✅ Draft legal notices
- ✅ Suggest strategies
- ✅ Handle payments
- ✅ Upload documents
- ❌ Cannot schedule hearings (judge only)
- ❌ Cannot access admin panel

### Judge
- ✅ View all cases
- ✅ Schedule hearings
- ✅ Draft judgments
- ✅ Detect contradictions
- ❌ Cannot create cases
- ❌ Cannot modify case details

### Admin
- ✅ Full system access
- ✅ View analytics
- ✅ Access audit logs
- ✅ Send notifications
- ✅ Manage all users and cases
- ✅ System configuration

---

## Common Issues & Solutions

### Issue: "No module named 'openai'"
**Solution:**
```bash
pip install openai>=1.0.0
```

### Issue: Database Connection Error
**Solution:**
```bash
# Check database connection
export SQLALCHEMY_DATABASE_URI="sqlite:///judicial.db"
# Or configure MySQL connection in .env
```

### Issue: JWT Token Expired
**Solution:**
```bash
# Use refresh endpoint to get new token
curl -X POST http://localhost:5000/auth/refresh \
  -H "Authorization: Bearer REFRESH_TOKEN"
```

### Issue: Rate Limit Exceeded
**Solution:**
Application enforces rate limits. Wait before retrying or use different IP/token.

### Issue: File Upload Failed
**Solution:**
- Ensure directory existence: `mkdir -p uploads/`
- Check file size (max 16MB default)
- Verify file type (pdf, png, jpg, jpeg, doc, docx)

---

## Performance Tips

1. **Database**: Create indexes on frequently queried columns
   ```sql
   CREATE INDEX idx_case_created_by ON case(created_by);
   CREATE INDEX idx_hearing_case ON hearing(case_id);
   ```

2. **Caching**: Enable Redis for production rate limiting
3. **API**: Use pagination for large result sets
   ```
   ?limit=50&offset=100
   ```

4. **AI**: Cache AI responses to reduce API calls

---

## Security Checklist

- ✅ Change all default secrets in production
- ✅ Use HTTPS in production
- ✅ Enable CORS only for trusted domains
- ✅ Use strong database passwords
- ✅ Protect uploads folder from direct access
- ✅ Enable rate limiting
- ✅ Monitor audit logs regularly
- ✅ Use environment variables for secrets
- ✅ Implement CSRF protection
- ✅ Keep OpenAI API key secure

---

## Files Structure

```
judicial_supreme_backend_v3/
├── app/
│   ├── __init__.py              # App factory
│   ├── config.py                # Configuration
│   ├── extensions.py            # Flask extensions
│   ├── models/                  # Database models
│   │   ├── user.py
│   │   ├── case.py
│   │   ├── hearing.py
│   │   ├── document.py
│   │   ├── payment.py
│   │   ├── notification.py
│   │   ├── audit.py
│   │   ├── case_activity.py
│   │   ├── ai_log.py
│   │   └── ...
│   ├── routes/                  # API endpoints
│   │   ├── auth.py
│   │   ├── case.py
│   │   ├── hearing.py
│   │   ├── payment.py
│   │   ├── document.py
│   │   ├── notification.py
│   │   ├── audit.py
│   │   └── case_activity.py
│   ├── ai/                      # AI features
│   │   ├── ai_client.py
│   │   ├── services.py
│   │   ├── routes.py
│   │   ├── prompt_builder.py
│   │   └── response_formatter.py
│   ├── middleware/              # RBAC middleware
│   │   └── rbac.py
│   ├── admin/                   # Admin features
│   │   └── routes.py
│   └── socket/                  # WebSocket
│       └── chat.py
├── tests/                       # Test suite
│   ├── conftest.py
│   ├── test_auth.py
│   └── test_comprehensive.py
├── migrations/                  # Database migrations
├── run.py                       # Development entry
├── wsgi.py                      # Production entry
├── requirements.txt             # Dependencies
└── README.md
```

---

## Support & Documentation

- **API Docs**: See `FIXES_AND_IMPROVEMENTS.md` for detailed changes
- **Full Endpoint List**: Check `app/routes/` directory
- **Database Models**: Check `app/models/` directory
- **AI Features**: Check `app/ai/` directory

---

## Version Info

- **Backend Version**: 3.0
- **Python Version**: 3.8+
- **Last Updated**: February 26, 2026
- **Status**: Production Ready ✅

---
