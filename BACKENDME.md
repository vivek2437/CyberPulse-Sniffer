# CyberPulse-Sniffe Backend (CICIDS2017)

Lightweight inference API that serves the pre-trained CICIDS2017 intrusion-detection model.

## Folder Structure
```
ml/
├─ main.py                 # FastAPI app exposing /health, /metadata, /predict
├─ requirements.txt        # Runtime dependencies for the inference server
├─ dataset/                # CICIDS2017 CSV parts (training data)
├─ model/
│  ├─ xgboost.pkl          # Default deployed model (tree depth=10, 200 estimators)
│  ├─ random_forest.pkl    # Alternative model (150 trees, max_depth=25)
│  └─ decision_tree.pkl    # Baseline model
├─ notebooks/
│  ├─ training.ipynb       # Original training notebook
│  └─ training.py          # Scripted export of the notebook
└─ results/
   ├─ model_results.csv    # Metrics per model and per class
   ├─ selected_features.csv# Top 30 features used for inference
   └─ all_feature_importances.csv
```

## Model Architecture
- Dataset: CICIDS2017 (multi-class intrusion detection).
- Feature selection: top 30 features from a 100-tree RandomForest selector (`results/selected_features.csv`).
- Default deployed model: XGBoost classifier (`model/xgboost.pkl`) with 200 trees, max_depth=10, learning_rate=0.1, subsample/colsample_bytree=0.8.
- Alternatives: RandomForest (150 trees, max_depth=25) and DecisionTree (max_depth=20); swap via `MODEL_PATH` env var.
- Labels (alphabetical order used by the label encoder):
  `BENIGN`, `Botnet`, `Botnet - Attempted`, `DDoS`, `DoS GoldenEye`, `DoS GoldenEye - Attempted`, `DoS Hulk`, `DoS Hulk - Attempted`, `DoS Slowhttptest`, `DoS Slowhttptest - Attempted`, `DoS Slowloris`, `DoS Slowloris - Attempted`, `FTP-Patator`, `FTP-Patator - Attempted`, `Heartbleed`, `Infiltration`, `Infiltration - Attempted`, `Infiltration - Portscan`, `Portscan`, `SSH-Patator`, `SSH-Patator - Attempted`, `Web Attack - Brute Force`, `Web Attack - Brute Force - Attempted`, `Web Attack - SQL Injection`, `Web Attack - SQL Injection - Attempted`, `Web Attack - XSS`, `Web Attack - XSS - Attempted`.

## Pictorial Architecture (text diagram)
```
[Next.js/React UI]
    |
    v
  HTTPS POST /predict (JSON: records[])
    |
    v
[FastAPI app in main.py]
    |
    v
  Feature alignment -> DataFrame (30 selected features)
    |
    v
[Loaded model: xgboost.pkl | random_forest.pkl | decision_tree.pkl]
    |
    v
  predict / predict_proba
    |
    v
[JSON response: predictions + probabilities]
```

## Results (from `results/model_results.csv`)
- XGBoost: Accuracy 0.99945, ROC_AUC 0.99979 (best overall).
- RandomForest: Accuracy 0.99944, ROC_AUC 0.97120.
- DecisionTree: Accuracy 0.99944, ROC_AUC 0.95283.
- Per-class correctness is included in `model_results.csv`; classes with lowest scores include rare Heartbleed/Infiltration variants.

## Running the API
1. Install deps (from `ml/`):
   ```bash
   pip install -r requirements.txt
   ```
2. Start the server (defaults to `model/xgboost.pkl`):
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000
   ```
3. Optional: choose a different model
   ```bash
   set MODEL_PATH=model/random_forest.pkl
   uvicorn main:app --host 0.0.0.0 --port 8000
   ```
4. Docs/UI: open `http://localhost:8000/docs` (Swagger) or `/redoc`.

## API
- `GET /health` → `{status, model}`
- `GET /metadata` → `{model_file, num_features, features[], class_labels[], predict_proba}`
- `POST /predict` → accepts `{"records": [ {<feature>: value, ...}, ... ] }`

### Example Request
```json
{
  "records": [
    {
      "Flow Duration": 12345,
      "Bwd Packet Length Std": 4.2,
      "Fwd Segment Size Avg": 15.7,
      "Packet Length Variance": 33.1
    }
  ]
}
```

### Example Response
```json
{
  "model": "xgboost.pkl",
  "predictions": ["BENIGN"],
  "class_probabilities": [
    {
      "BENIGN": 0.91,
      "Botnet": 0.01,
      "Portscan": 0.02
    }
  ]
}
```
(Probabilities include all known classes; omitted here for brevity.)

### Next.js/React Fetch Snippet
```ts
const payload = {
  records: [
    {
      "Flow Duration": 12345,
      "Bwd Packet Length Std": 4.2,
      "Fwd Segment Size Avg": 15.7,
      "Packet Length Variance": 33.1,
    },
  ],
};

const res = await fetch("http://localhost:8000/predict", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify(payload),
});

if (!res.ok) throw new Error("prediction failed");
const data = await res.json();
console.log(data.predictions[0]);
```

## Notes & Future Work
- Add input validation against expected ranges (e.g., non-negative durations, capped packet lengths).
- Persist a saved `LabelEncoder` to remove any risk of label/order drift.
- Add streaming or batch scoring endpoints if throughput requirements grow.
- Consider quantizing or distilling the model for edge deployment.
- Add CI checks and unit tests for the API contract and model loading.
