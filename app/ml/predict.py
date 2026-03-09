"""Predictor wrapper to load model and produce human-friendly predictions."""
from pathlib import Path
import joblib
import json
from datetime import datetime
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
MODELS_DIR = ROOT / "models"
MODEL_FILE = MODELS_DIR / "delay_model_v1.joblib"
META_FILE = MODELS_DIR / "model_metadata.json"

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

class Predictor:
    def __init__(self, model_path=None, meta_path=None):
        self.model_path = model_path or MODEL_FILE
        self.meta_path = meta_path or META_FILE
        self.model = None
        self.meta = None
        self.mappings = {}
        self._load()

    def _load(self):
        try:
            self.model = joblib.load(self.model_path)
        except Exception:
            self.model = None
        try:
            with open(self.meta_path, "r", encoding="utf-8") as fh:
                self.meta = json.load(fh)
                self.mappings = self.meta.get("mappings", {})
        except Exception:
            self.meta = None

    def _encode(self, sample: dict):
        row = []
        for f in FEATURE_LIST:
            v = sample.get(f)
            if f in self.mappings:
                m = self.mappings[f]
                v = m.get(v, m.get("__default", 0))
            row.append(v if v is not None else 0)
        return np.array(row).reshape(1, -1)

    def _get_thresholds(self):
        # read from Flask config if available, else use defaults
        try:
            from flask import current_app
            low = current_app.config.get("LOW_DELAY_THRESHOLD", 365)
            high = current_app.config.get("HIGH_DELAY_THRESHOLD", 900)
        except Exception:
            low = 365
            high = 900
        return low, high

    def predict(self, sample: dict):
        if self.model is None:
            raise RuntimeError("Model not loaded")
        x = self._encode(sample)
        pred = float(self.model.predict(x)[0])
        # confidence proxy: inverse normalized variance from trees
        try:
            # For RandomForest, use std of predictions from trees
            all_preds = np.array([t.predict(x)[0] for t in self.model.estimators_])
            std = float(all_preds.std())
            conf = max(0.0, 1.0 - std / max(1.0, abs(pred)))
        except Exception:
            conf = 0.5

        days = int(round(pred))
        years = round(pred / 365.0, 2)
        low, high = self._get_thresholds()
        if days < low:
            risk = "Low Delay"
        elif days <= high:
            risk = "Moderate Delay"
        else:
            risk = "High Delay"

        res = {
            "predicted_duration_days": days,
            "predicted_duration_years": years,
            "risk_level": risk,
            "model_version": (self.meta.get("model_version") if self.meta else "v1"),
            "confidence": round(float(conf), 3),
            "generated_at": datetime.utcnow().isoformat(),
        }
        return res


# module-level predictor for easy import
predictor = Predictor()  # may raise if files missing
