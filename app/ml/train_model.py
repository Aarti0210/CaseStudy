"""Training pipeline for delay prediction model.

Saves trained model to models/delay_model_v1.joblib and metadata json.
If no dataset is found, generates a synthetic dataset and saves CSV.
"""
from pathlib import Path
import json
import time
from datetime import datetime
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import joblib

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data"
MODELS_DIR = ROOT / "models"
META_FILE = MODELS_DIR / "model_metadata.json"
MODEL_FILE = MODELS_DIR / "delay_model_v1.joblib"
CSV_FILE = DATA_DIR / "delay_dataset.csv"

FEATURE_LIST = [
    "case_type",
    "number_of_hearings",
    "judge_workload",
    "document_count",
    "case_priority",
    "filing_to_first_hearing_days",
    "court_level",
    "previous_adjournments",
]

CATEGORICALS = ["case_type", "case_priority", "court_level"]


def generate_synthetic(n=2000, seed=42):
    np.random.seed(seed)
    case_types = ["civil", "criminal", "family", "tax", "labor"]
    priorities = ["low", "medium", "high"]
    court_levels = ["magistrate", "district", "high_court", "supreme"]

    rows = []
    for i in range(n):
        case_type = np.random.choice(case_types, p=[0.4, 0.3, 0.15, 0.1, 0.05])
        number_of_hearings = int(np.random.poisson(3) + 1)
        judge_workload = max(1, int(np.random.normal(50, 15)))
        document_count = int(np.random.poisson(5))
        case_priority = np.random.choice(priorities, p=[0.6, 0.3, 0.1])
        filing_to_first_hearing_days = abs(int(np.random.exponential(30)))
        court_level = np.random.choice(court_levels, p=[0.5, 0.35, 0.1, 0.05])
        previous_adjournments = int(np.random.poisson(1))

        # basic heuristic for duration: base by court level and case type
        base = {
            "magistrate": 180,
            "district": 365,
            "high_court": 720,
            "supreme": 1200,
        }[court_level]
        # multipliers
        m_type = {"civil": 1.0, "criminal": 1.2, "family": 0.9, "tax": 1.3, "labor": 1.1}[case_type]
        m_priority = {"low": 0.9, "medium": 1.0, "high": 1.2}[case_priority]
        noise = int(np.random.normal(0, 90))
        duration = max(30, int(base * m_type * m_priority + number_of_hearings * 15 + previous_adjournments * 30 - judge_workload * 0.1 + filing_to_first_hearing_days * 0.5 + noise))

        rows.append(
            {
                "case_type": case_type,
                "number_of_hearings": number_of_hearings,
                "judge_workload": judge_workload,
                "document_count": document_count,
                "case_priority": case_priority,
                "filing_to_first_hearing_days": filing_to_first_hearing_days,
                "court_level": court_level,
                "previous_adjournments": previous_adjournments,
                "total_case_duration_days": duration,
            }
        )
    df = pd.DataFrame(rows)
    return df


def prepare_data(df: pd.DataFrame):
    # map categoricals to ints and store mappings
    mappings = {}
    df2 = df.copy()
    for c in CATEGORICALS:
        vals = sorted(df2[c].unique())
        m = {v: i + 1 for i, v in enumerate(vals)}
        m["__default"] = 0
        mappings[c] = m
        df2[c] = df2[c].map(lambda x: m.get(x, 0))

    X = df2[FEATURE_LIST]
    y = df2["total_case_duration_days"]
    return X, y, mappings


def train(n_samples=2000, use_csv=True):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    MODELS_DIR.mkdir(parents=True, exist_ok=True)

    if use_csv and CSV_FILE.exists():
        df = pd.read_csv(CSV_FILE)
    else:
        df = generate_synthetic(n_samples)
        df.to_csv(CSV_FILE, index=False)

    X, y, mappings = prepare_data(df)

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = RandomForestRegressor(n_estimators=200, random_state=42, n_jobs=-1)

    # cross val
    cv_scores = cross_val_score(model, X_train, y_train, cv=5, scoring="neg_mean_squared_error", n_jobs=-1)
    cv_rmse = float(np.mean(np.sqrt(np.abs(-cv_scores))))

    model.fit(X_train, y_train)

    preds = model.predict(X_test)
    mse = mean_squared_error(y_test, preds)
    rmse = float(np.sqrt(mse))
    mae = mean_absolute_error(y_test, preds)
    r2 = r2_score(y_test, preds)

    # feature importance
    importances = model.feature_importances_.tolist()
    feature_importance = sorted(zip(FEATURE_LIST, importances), key=lambda x: x[1], reverse=True)

    # save model
    joblib.dump(model, MODEL_FILE)

    metadata = {
        "model_version": "v1",
        "trained_at": datetime.utcnow().isoformat(),
        "dataset_size": int(len(df)),
        "train_size": int(len(X_train)),
        "test_size": int(len(X_test)),
        "metrics": {"rmse": float(rmse), "mae": float(mae), "r2": float(r2), "cv_rmse": float(cv_rmse)},
        "feature_list": FEATURE_LIST,
        "mappings": mappings,
        "feature_importance": [{"feature": f, "importance": float(im)} for f, im in feature_importance],
    }
    with open(META_FILE, "w", encoding="utf-8") as fh:
        json.dump(metadata, fh, indent=2)

    print("Training complete")
    print(json.dumps(metadata["metrics"], indent=2))
    print("Top features:")
    for f, imp in feature_importance[:10]:
        print(f, imp)

    return MODEL_FILE, META_FILE


if __name__ == "__main__":
    train()
