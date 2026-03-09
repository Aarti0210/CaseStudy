# Judicial Supreme Backend (Scaffold)

Run locally (development):

````markdown
# Judicial Supreme Backend

Overview
--------
This Flask backend provides API endpoints for a judicial case management demo and includes an integrated machine learning component used to predict case delays. The ML component is a RandomForest regressor packaged as a versioned artifact (model_version: v1).

Quick start (development)
-------------------------
```bash
cp .env.example .env
# edit .env (set DB and JWT secrets)
pip install -r requirements.txt
python run.py
```

Production (Gunicorn)
---------------------
```bash
gunicorn wsgi:app -k eventlet -w 1 -b 0.0.0.0:8000
```

Docker
------
```bash
docker build -t judicial-backend .
docker run -p 8000:8000 --env-file .env -v $(pwd)/uploads:/app/uploads judicial-backend

> **NOTE:** When deploying to Render Free (or any ephemeral container), the `uploads` directory
> lives inside the container and will be wiped on every redeploy. Use external storage for
> anything you need to keep long term.
```

Model note
----------
Model v1 is frozen for the DIPEX demo. Retraining is offline only — see `DIPEX_DEMO_GUIDE.md` for retraining instructions and notes about productionizing a retraining pipeline.

See `API_REFERENCE.md` and `QUICK_START.md` for API usage and demo instructions.
````
