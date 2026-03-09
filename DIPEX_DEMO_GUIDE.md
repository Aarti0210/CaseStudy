# DIPEX Demo Guide

Project summary
---------------
This repository provides a Flask-based backend for a judicial case management demo with an integrated supervised ML component that predicts case delay. The model is a RandomForest regressor saved as `models/delay_model_v1.joblib` (version `v1`). The API exposes a protected ML endpoint for predictions and a metadata endpoint for transparency.

How to start the server
-----------------------
1. Create and edit `.env` from `.env.example` and set required env vars (DB, JWT secrets).
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run the application (development):

```bash
python run.py
```

Server will be available at `http://localhost:5000`.

How to train the model (offline)
---------------------------------
1. Training is performed offline using `app/ml/train_model.py`.
2. Run the script in a controlled environment (not in production) to generate a new `delay_model_v1.joblib` and `model_metadata.json`:

```bash
python app/ml/train_model.py
```

3. Replace the artifact in `models/` and restart the service to pick up the new model.

How to test the `predict-delay` endpoint
----------------------------------------
1. Obtain a JWT for a permitted role (admin, judge or lawyer).
2. Call the endpoint:

```bash
curl -X POST http://localhost:5000/ai/predict-delay \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"case_data": {"case_type":"civil","number_of_hearings":3,"judge_workload":40,"document_count":5,"case_priority":"medium","filing_to_first_hearing_days":20,"court_level":"district","previous_adjournments":1}}'
```

How to show `model-info` to judges
---------------------------------
1. `GET /ai/model-info` is restricted to admin role. For judges, display the model metadata from the UI ahead of the demo, or show a read-only snapshot.
2. As admin, run:

```bash
curl -X GET http://localhost:5000/ai/model-info \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

Key technical highlights
------------------------
- Deterministic ML model (RandomForest) for numeric delay prediction.
- Versioned artifact (`model_version: v1`) to ensure reproducibility.
- Risk classification derived from predicted days using configurable thresholds (`LOW_DELAY_THRESHOLD`, `HIGH_DELAY_THRESHOLD`).
- Metadata endpoint provides RMSE/MAE/r2 and feature list for transparency.
- JWT authentication and RBAC protect AI endpoints.

Suggested live demo flow
------------------------
1. Quick project intro (1 minute): explain model purpose and governance.
2. Show `GET /` health endpoint and confirm server is running.
3. Show `GET /ai/model-info` (admin) — display training samples, metrics, model_version.
4. Run `POST /ai/predict-delay` with a prepared case (judge or admin token) and highlight predicted days, `risk_level`, `confidence`, and `model_version`.
5. Explain thresholds and how they map to risk levels; optionally tweak config offline to demonstrate sensitivity.
6. Show fallback LLM features (case summary) to demonstrate full AI stack.
7. Close with transparency notes and next steps for productionization.

Notes
-----
- Model v1 is frozen for DIPEX — any retraining must be performed offline and redeployed intentionally.
- Do not expose JWT secrets or place production keys in the repository.

*** End of Guide ***
