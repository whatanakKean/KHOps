# 🚀 Model Training & Serving Guide

## Quick Reference

### Train a Model (3 Ways)

**1. Direct CLI Training**
```bash
khops train start data/training.csv \
  --name my-model \
  --version 1.0.0 \
  --target target_column \
  --algorithm random_forest \
  --stage dev
```

**2. Pipeline-Based Training**
```bash
khops run examples/pipelines/sample_pipeline.yaml
```

**3. AutoML Comparison**
```bash
khops automl run examples/pipelines/sample_pipeline.yaml \
  --algorithms "random_forest,logistic_regression,xgboost_classifier"
```

---

## How Training Works

### Architecture: DAG Pipeline Executor

Training follows a **Directed Acyclic Graph (DAG)** pattern with sequential node execution:

```
┌─────────────────┐
│  Data Loading   │ (CSV/JSON → DataFrame)
│  (data node)    │
└────────┬────────┘
         │
┌────────▼────────┐
│ Data Prep       │ (drop nulls, normalize, encode)
│ (data node)     │
└────────┬────────┘
         │
┌────────▼────────┐
│ Model Training  │ (fit classifier on 75% data)
│ (training node) │
└────────┬────────┘
         │
┌────────▼────────┐
│ Model Eval      │ (compute metrics on 25% test data)
│ (eval node)     │
└─────────────────┘
```

### Node Types

**1. Data Nodes** - Load and transform data
```yaml
- id: data_load
  type: data
  params:
    source: "./data/training.csv"
    operations:
      - drop_nulls      # Remove missing values
      - normalize       # Scale to 0-1 range
      - encode          # One-hot encoding
      - fill_missing    # Fill NaN with 0
```

**2. Training Nodes** - Fit predictive models
```yaml
- id: model_train
  type: training
  params:
    algorithm: "random_forest"    # Classification or regression
    target: "target"              # Column to predict
    n_estimators: 100             # Tree count (RF specific)
    max_depth: 10                 # Max tree depth (RF specific)
```

**3. Evaluation Nodes** - Compute metrics
```yaml
- id: model_eval
  type: evaluation
  params:
    target: "target"
    metrics:
      - accuracy
      - precision
      - recall
```

---

## Training Pipeline Execution

### Step 1: Data Loading
- Reads CSV/JSON file into pandas DataFrame
- Returns: `{dataframe, row_count, columns}`

### Step 2: Data Preparation
- Receives DataFrame from parent node
- Applies operations sequentially:
  - **drop_nulls**: `df.dropna()`
  - **normalize**: Min-max scaling per numeric column
  - **encode**: `pd.get_dummies()` for categorical columns
  - **fill_missing**: `df.fillna(0)`
- Returns: `{dataframe, row_count, columns}`

### Step 3: Model Training
- Extracts features (X) and target (y)
- **Splits Data**: 75% train, 25% test (random_state=42)
- **Trains Model**: Calls `model.fit(X_train, y_train)`
- **Evaluates**: `predictions = model.predict(X_test)`
- **Saves Artifact**: Pickle file to `/models/` directory
- Returns: `{trained, algorithm, model_path, metrics, row_count}`

### Step 4: Model Evaluation
- Loads trained model from pickle
- Runs inference on full dataset
- Computes metrics (accuracy, precision, recall, etc.)
- Returns: `{evaluated, metrics, target, metric_names}`

---

## Supported Algorithms

### Classification
```python
"random_forest"          # sklearn.ensemble.RandomForestClassifier
"logistic_regression"    # sklearn.linear_model.LogisticRegression
"xgboost_classifier"     # xgboost.XGBClassifier
"gradient_boosting"      # sklearn.ensemble.GradientBoostingClassifier
```

### Regression
```python
"random_forest_regression"    # sklearn.ensemble.RandomForestRegressor
"linear_regression"          # sklearn.linear_model.LinearRegression
"xgboost_regression"         # xgboost.XGBRegressor
```

---

## Model Registration

After training completes, model is automatically registered:

```python
Model(
    name="my-model",
    version="1.0.0",
    stage="dev",
    path="/models/my-model_1.0.0_20260410124530.pkl",
    framework="sklearn",
    metrics={"accuracy": 0.85, "precision": 0.82, "recall": 0.80},
    tags=["phase5", "production-ready"],
    metadata={"n_estimators": 100, "max_depth": 10}
)
```

### Fields
- **name**: Model identifier
- **version**: Semantic version (1.0.0, 1.0.1)
- **stage**: Current deployment stage (dev/staging/production/archived)
- **path**: Filesystem path to pickle artifact
- **framework**: ML framework (sklearn, xgboost, tensorflow)
- **metrics**: Performance metrics from training
- **tags**: Custom categorization tags
- **metadata**: Hyperparameters and training config

---

## Model Promotion Workflow

Stage progression with audit trail:

```bash
# Initial state
khops models list
# my-model @ 1.0.0 (dev)

# Promote to staging (after validation)
khops models promote my-model --version 1.0.0 --stage staging
# my-model @ 1.0.0 (staging) ← audit recorded

# Promote to production (after testing)
khops models promote my-model --version 1.0.0 --stage production
# my-model @ 1.0.0 (production) ← audit recorded

# View promotion history
khops models history my-model --version 1.0.0
# dev → staging (promoted by: user1, reason: "passed validation")
# staging → production (promoted by: devops, reason: "A/B passed")

# Rollback if issues found
khops models rollback my-model --version 1.0.0
# Reverts to previous version in production

# Retire old models
khops models retire my-model --version 0.9.0
# Marks as archived
```

---

## How Serving Works

### Model Serving Architecture

```
Request → API Handler → Serving Service → Model Cache → Predictions → Response
                              ↓
                        [Load Model]
                              ↓
                        [Check Cache]
                         /          \
                        /            \
                File not changed   File changed
                (use cached)       (reload & cache)
```

### Serving Endpoints

**Make Predictions**
```bash
curl -X POST http://localhost:8001/api/v1/serve/my-model \
  -H "Content-Type: application/json" \
  -d '{
    "features": [
      {"feature1": 5.1, "feature2": 3.5}
    ]
  }'

# Response
{
  "model_name": "my-model",
  "version": "1.0.0",
  "stage": "production",
  "predictions": [0],
  "input_count": 1,
  "created_at": "2026-04-10T10:00:00",
  "updated_at": "2026-04-10T10:00:00"
}
```

**Get Model Metadata**
```bash
curl http://localhost:8001/api/v1/serve/my-model/metadata?stage=production

{
  "model_name": "my-model",
  "version": "1.0.0",
  "stage": "production",
  "path": "/models/my-model_1.0.0.pkl",
  "metrics": {"accuracy": 0.85},
  "metadata": {"n_estimators": 100},
  "created_at": "2026-04-10T10:00:00",
  "updated_at": "2026-04-10T10:00:00"
}
```

**Check Health**
```bash
curl http://localhost:8001/api/v1/serve/my-model/health

{
  "model_name": "my-model",
  "version": "1.0.0",
  "stage": "production",
  "status": "available",
  "last_updated": "2026-04-10T10:00:00"
}
```

### Model Loading Process

```python
# 1. Query Database
model = db.query(Model).filter(Model.name == "my-model", Model.stage == "production").first()

# 2. Check Cache
cache_key = "/models/my-model_1.0.0.pkl"
file_mtime = os.stat(cache_key).st_mtime  # Last modified time

if cache[cache_key]["mtime"] == file_mtime:
    model = cache[cache_key]["model"]  # Use cached
else:
    # 3. Load from Disk
    with open(cache_key, "rb") as f:
        model = pickle.load(f)

    # 4. Update Cache
    cache[cache_key] = {"model": model, "mtime": file_mtime}

# 5. Make Prediction
features_df = pd.DataFrame(request.features)
predictions = model.predict(features_df)

# 6. Return Response
{
  "model_name": "my-model",
  "predictions": predictions.tolist()
}
```

### Model Selection Strategy

```bash
# Query by name (gets latest version in production)
GET /serve/my-model
# → Returns: production version (by created_at DESC)

# Query by version
GET /serve/my-model?version=1.0.0
# → Returns: specific version

# Query by stage
GET /serve/my-model?stage=staging
# → Returns: latest staging version

# Query by version AND stage
GET /serve/my-model?version=1.0.0&stage=production
# → Returns: exact match or 404
```

---

## Performance Features

### In-Memory Caching
- **Benefit**: Fast inference (microseconds), no disk reads
- **Auto-Refresh**: Detects file changes via `mtime` check
- **Zero Downtime**: Models update automatically when file changes

### Data Flow
```
1. Load model once → Cache to memory
2. Per-request inference: Just call model.predict()
3. File changed? Auto-reload and re-cache
```

### Metrics
- First request: ~100-500ms (file I/O + unpickling)
- Subsequent requests: <1ms (cached inference)
- Model update: 1-2 requests to detect and reload

---

## Complete Example: Train to Serve

### 1. Create Sample Pipeline
```yaml
# examples/pipelines/sample_pipeline.yaml
name: sample_pipeline
nodes:
  - id: data_load
    type: data
    params:
      source: "./examples/data/raw/training_data.csv"

  - id: data_prep
    type: data
    params:
      operations: [drop_nulls, normalize]

  - id: model_train
    type: training
    params:
      algorithm: random_forest
      target: target
      n_estimators: 100

  - id: model_eval
    type: evaluation
    params:
      target: target
      metrics: [accuracy, precision, recall]

edges:
  - from: data_load
    to: data_prep
  - from: data_prep
    to: model_train
  - from: model_train
    to: model_eval
```

### 2. Execute Pipeline
```bash
khops run examples/pipelines/sample_pipeline.yaml
# Training outputs:
# ✅ Model trained with accuracy: 0.85
# ✅ Saved to: /models/sample_pipeline_20260410_124530.pkl
# ✅ Registered: sample_pipeline @ 1.0.0 (dev)
```

### 3. Promote to Production
```bash
khops models promote sample_pipeline --version 1.0.0 --stage production
# ✅ Promoted sample_pipeline/1.0.0 to production
```

### 4. Start Serving API
```bash
khops serve
# Server running on http://localhost:8001
# Serving API ready on /api/v1/serve/
```

### 5. Make Predictions
```bash
curl -X POST http://localhost:8001/api/v1/serve/sample_pipeline \
  -H "Content-Type: application/json" \
  -d '{"features": [{"feature1": 5.1, "feature2": 3.5}]}'

# Response:
{
  "model_name": "sample_pipeline",
  "version": "1.0.0",
  "stage": "production",
  "predictions": [1],
  "input_count": 1
}
```

---

## Key Takeaways

✅ **Training**: DAG-based pipeline with 3 node types (data, training, eval)
✅ **Versioning**: Semantic versions with promotion audit trail
✅ **Serving**: Fast in-memory caching with auto-refresh on file changes
✅ **Flexibility**: Support multiple algorithms and data operations
✅ **Observability**: Metrics tracking, drift detection, and alerts
✅ **Production Ready**: Health checks, metadata, stage-aware routing

---

## Related Documentation

- [Phase 5 Completion](PHASE5_COMPLETION.md) - Full feature summary
- [khops/pipelines/executor.py](../khops/pipelines/executor.py) - DAG executor implementation
- [khops/server/routes/serving.py](../khops/server/routes/serving.py) - Serving API definition
- [khops/server/services/serving_service.py](../khops/server/services/serving_service.py) - Caching logic
- [examples/pipelines/sample_pipeline.yaml](../examples/pipelines/sample_pipeline.yaml) - Example config
