"""
Quick API reference for Judicial Supreme Backend
================================================

Base URL: http://localhost:5000

AVAILABLE ENDPOINTS:
===================

✅ HEALTH CHECK
  GET  /                        - Server status & available endpoints

✅ AUTHENTICATION (Auth Module)
  POST /auth/signup             - Register new user
  POST /auth/login              - Login user
  POST /auth/refresh            - Refresh JWT token
  POST /auth/logout             - Logout user

✅ CASES (Case Management)
  GET  /case                    - List all cases
  POST /case                    - Create new case
  GET  /case/<id>               - Get case details
  PUT  /case/<id>               - Update case
  DELETE /case/<id>             - Delete case

✅ HEARINGS (Court Hearings)
  GET  /hearing                 - List all hearings
  POST /hearing                 - Schedule hearing
  GET  /hearing/<id>            - Get hearing details
  PUT  /hearing/<id>            - Update hearing

✅ DOCUMENTS (Case Documents)
  GET  /document                - List documents
  POST /document                - Upload document
  GET  /document/<id>           - Download document
  DELETE /document/<id>         - Delete document

✅ PAYMENTS (Payment Processing)
  GET  /payment                 - List payments
  POST /payment                 - Record payment
  GET  /payment/<id>            - Get payment details

✅ NOTIFICATIONS (User Notifications)
  GET  /notification            - List notifications
  POST /notification            - Create notification
  PUT  /notification/<id>/read  - Mark as read

✅ ACTIVITY (Case Activity Log)
  GET  /activity                - List case activities
  POST /activity                - Log activity

✅ AUDIT (Audit Logs)
  GET  /audit                   - List audit logs

✅ AI SERVICES (Artificial Intelligence)
  POST /ai/explain-order        - Explain a court order (LLM)
  POST /ai/case-summary         - Generate case summary (LLM)
  POST /ai/predict-delay        - Predict case delay (ML model, RandomForest v1)
  GET  /ai/model-info           - Retrieve ML model metadata (admin only)

✅ ADMIN (Administration)
  GET  /admin                   - Admin dashboard
  POST /admin/users             - Manage users

TESTING EXAMPLES:
================

# Test server is running
curl http://localhost:5000/

# Register new user
curl -X POST http://localhost:5000/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"name":"John Doe","email":"john@example.com","password":"pass123","role":"lawyer"}'

# Login
curl -X POST http://localhost:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"john@example.com","password":"pass123"}'

# Get cases
curl http://localhost:5000/case \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

### ML & Model endpoints

Predict delay (ML model v1):
```bash
curl -X POST http://localhost:5000/ai/predict-delay \
  -H "Authorization: Bearer YOUR_ADMIN_OR_JUDGE_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"case_data": {"case_type":"civil","number_of_hearings":3,"judge_workload":40,"document_count":5,"case_priority":"medium","filing_to_first_hearing_days":20,"court_level":"district","previous_adjournments":1}}'
```

Model info (admin only):
```bash
curl -X GET http://localhost:5000/ai/model-info \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

Notes:
- Risk levels are computed by comparing the predicted duration (days) against two thresholds: `LOW_DELAY_THRESHOLD` and `HIGH_DELAY_THRESHOLD` configured in `app.config` (defaults: 365 / 900 days).
- Model v1 is frozen for the DIPEX demo. Retraining is offline and performed via `app/ml/train_model.py`.

DATABASE:
=========
Server: sql.freedb.tech
Database: freedb_Quick_Justice
Tables: 13 (user, role, case, hearing, document, payment, notification, otp, ai_log, audit_log, billing, case_activity, chat_message)

CONNECTION STATUS:
==================
✅ Backend: Running
✅ Database: Connected (FreeDB)
✅ SocketIO: Enabled
✅ JWT Auth: Enabled
✅ Rate Limiting: Enabled
✅ CORS: Enabled
