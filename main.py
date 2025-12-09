"""FastAPI inference service for the CICIDS2017 intrusion-detection models.

The service loads a trained tree-based classifier (default: XGBoost) and exposes
HTTP endpoints that are friendly to Next.js/React frontends. Clients send one or
more network-flow feature dictionaries and receive predicted labels plus class
probabilities.
"""

from pathlib import Path
from typing import Dict, List, Optional

import os

import joblib
import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field


BASE_DIR = Path(__file__).resolve().parent
ENV_MODEL_PATH = os.getenv("MODEL_PATH")
DEFAULT_MODEL_PATH = Path(ENV_MODEL_PATH).expanduser() if ENV_MODEL_PATH else BASE_DIR / "model" / "xgboost.pkl"
FEATURE_LIST_PATH = BASE_DIR / "results" / "selected_features.csv"

# Label names in the order produced by LabelEncoder (alphabetical on the raw labels)
CLASS_NAMES = [
    "BENIGN",
    "Botnet",
    "Botnet - Attempted",
    "DDoS",
    "DoS GoldenEye",
    "DoS GoldenEye - Attempted",
    "DoS Hulk",
    "DoS Hulk - Attempted",
    "DoS Slowhttptest",
    "DoS Slowhttptest - Attempted",
    "DoS Slowloris",
    "DoS Slowloris - Attempted",
    "FTP-Patator",
    "FTP-Patator - Attempted",
    "Heartbleed",
    "Infiltration",
    "Infiltration - Attempted",
    "Infiltration - Portscan",
    "Portscan",
    "SSH-Patator",
    "SSH-Patator - Attempted",
    "Web Attack - Brute Force",
    "Web Attack - Brute Force - Attempted",
    "Web Attack - SQL Injection",
    "Web Attack - SQL Injection - Attempted",
    "Web Attack - XSS",
    "Web Attack - XSS - Attempted",
]


def load_selected_features(path: Path) -> List[str]:
    if not path.exists():
        raise FileNotFoundError(f"Selected feature list missing at {path}")
    df = pd.read_csv(path)
    if "TopFeatures" not in df.columns:
        raise ValueError("selected_features.csv must contain a 'TopFeatures' column")
    return df["TopFeatures"].tolist()


def load_model(path: Path):
    if not path.exists():
        raise FileNotFoundError(f"Model file not found at {path}")
    return joblib.load(path)


SELECTED_FEATURES = load_selected_features(FEATURE_LIST_PATH)
MODEL = load_model(DEFAULT_MODEL_PATH)


class PredictRequest(BaseModel):
    records: List[Dict[str, float]] = Field(..., description="List of feature dictionaries keyed by column name")


class PredictResponse(BaseModel):
    model: str
    predictions: List[str]
    class_probabilities: Optional[List[Dict[str, float]]] = None


app = FastAPI(
    title="CICIDS2017 Intrusion Detection API",
    version="1.0.0",
    description="Lightweight inference service for the pre-trained CICIDS2017 models",
)


def _build_frame(records: List[Dict[str, float]]) -> pd.DataFrame:
    rows = []
    for record in records:
        row = [float(record.get(col, 0.0)) for col in SELECTED_FEATURES]
        rows.append(row)
    return pd.DataFrame(rows, columns=SELECTED_FEATURES)


def _map_label(class_id: int) -> str:
    if 0 <= class_id < len(CLASS_NAMES):
        return CLASS_NAMES[class_id]
    return str(class_id)


@app.get("/health")
def health_check() -> Dict[str, str]:
    return {"status": "ok", "model": DEFAULT_MODEL_PATH.name}


@app.get("/metadata")
def metadata() -> Dict[str, object]:
    return {
        "model_file": str(DEFAULT_MODEL_PATH.name),
        "num_features": len(SELECTED_FEATURES),
        "features": SELECTED_FEATURES,
        "class_labels": CLASS_NAMES,
        "predict_proba": hasattr(MODEL, "predict_proba"),
    }


@app.post("/predict", response_model=PredictResponse)
def predict(payload: PredictRequest) -> PredictResponse:
    if not payload.records:
        raise HTTPException(status_code=400, detail="records must not be empty")

    frame = _build_frame(payload.records)
    try:
        class_ids = MODEL.predict(frame)
    except Exception as exc:  # pragma: no cover - defensive guard
        raise HTTPException(status_code=500, detail=f"Model inference failed: {exc}")

    predictions = [_map_label(int(cid)) for cid in class_ids]

    class_probabilities: Optional[List[Dict[str, float]]] = None
    if hasattr(MODEL, "predict_proba"):
        probs = MODEL.predict_proba(frame)
        class_probabilities = []
        for row in probs:
            class_probabilities.append({CLASS_NAMES[i]: float(p) for i, p in enumerate(row) if i < len(CLASS_NAMES)})

    return PredictResponse(
        model=DEFAULT_MODEL_PATH.name,
        predictions=predictions,
        class_probabilities=class_probabilities,
    )


@app.get("/")
def root() -> Dict[str, str]:
    return {"message": "CICIDS2017 intrusion-detection backend is running", "docs": "/docs"}