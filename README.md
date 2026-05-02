# 🌌 KHOps: High-Performance MLOps Platform

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python: 3.9+](https://img.shields.io/badge/Python-3.9+-darkgreen.svg)](https://www.python.org/)
[![UI: Synthetix Dark](https://img.shields.io/badge/UI-Synthetix_Dark-blueviolet.svg)](#design-principles)

**KHOps** is an open-source platform designed to streamline the entire machine learning lifecycle, from development to deployment and monitoring.

---

## 🌌 KHOps Core Platform Features

---

## 📊 1. Dashboard

**Goal:** Central control panel for ML lifecycle visibility

- 📈 **System Overview**
  - Active pipelines status
  - Model deployment health
  - Resource usage snapshot (CPU/GPU/RAM)

- 🚀 **Quick Actions**
  - Trigger pipeline runs
  - Deploy latest model version
  - Upload dataset for analysis

- 🔔 **Alerts & Notifications**
  - Drift alerts
  - Pipeline failure alerts
  - Latency/anomaly notifications

- 📉 **Performance Summary**
  - Model accuracy trends
  - P95 latency overview
  - Data quality score snapshot

---

## 🔁 2. Pipelines

**Goal:** End-to-end ML workflow orchestration

- 🧩 **Pipeline Builder**
  - Drag-and-drop DAG editor
  - Prebuilt ML blocks (ingest → train → evaluate → deploy)

- ⚙️ **Execution Engine**
  - Scheduled runs (cron-based)
  - On-demand execution
  - Parallel task processing

- 🔄 **Workflow Management**
  - Retry/failure handling
  - Versioned pipeline definitions
  - Dependency tracking

- 🧪 **Pipeline Stages**
  - Data ingestion
  - Feature engineering
  - Model training
  - Evaluation & validation
  - Deployment step

---

## 📂 3. Data Explorer (📊 Data Profiling Engine)

**Goal:** Upload CSV → instant deep data quality & structure report

- 📤 **Data Upload Interface**
  - CSV / Parquet support
  - Schema auto-detection

- 🔍 **Automated Data Profiling (powered by YData-style profiling)**
  - Missing value analysis
  - Duplicate detection
  - Column type inference
  - Distribution analysis (histograms, skewness, kurtosis)
  - Correlation matrix
  - Outlier detection

- 📊 **Data Quality Report**
  - Completeness score
  - Consistency score
  - Data drift indicators
  - Summary statistics report

- 🧠 **Smart Insights**
  - “This column is highly skewed”
  - “Potential leakage detected”
  - “Highly correlated features detected”

---

## 🧾 4. Model Registry

**Goal:** Central system for versioning and managing ML models

- 🏷️ **Model Versioning**
  - Model artifacts tracking
  - Version comparison
  - Stage transitions (dev → staging → prod)

- 📦 **Artifact Storage**
  - Model binaries
  - Preprocessing pipelines
  - Feature schemas

- 🔗 **Lineage Tracking**
  - Dataset → experiment → model traceability
  - Training configuration history

- 🧪 **Model Evaluation Logs**
  - Metrics history (accuracy, F1, AUC, etc.)
  - Benchmark comparisons

---

## 📡 5. Monitoring

**Goal:** Real-time observability for models + pipelines

- 📉 **Model Performance Monitoring**
  - Accuracy decay tracking
  - Prediction confidence distribution
  - Drift detection (data + concept drift)

- ⚡ **System Monitoring**
  - API latency (P50 / P95 / P99)
  - Error rates
  - Throughput (requests/sec)

- 🧠 **Data Drift Engine**
  - KS test monitoring
  - Feature distribution shift detection
  - Real-time alerts

- 🚨 **Alerting System**
  - Slack / Email / Webhook alerts
  - Threshold-based triggers
  - Anomaly detection alerts

---



## 🚀 System Architecture
<img width="1440" height="1948" alt="image" src="https://github.com/user-attachments/assets/bd370497-ec68-4f46-b96d-6b4d9df9a3f1" />

## 📊 Folder Structure

<pre>
khops/
│
├── README.md
├── LICENSE
├── pyproject.toml
├── setup.cfg
├── Makefile
├── .gitignore
├── .env.example
│
├── docs/                          # 📚 Documentation
│   ├── index.md
│   ├── architecture.md
│   ├── dashboard.md
│   ├── pipelines.md
│   ├── data_explorer.md
│   ├── registry.md
│   ├── monitoring.md
│   ├── artifacts.md
│   ├── api_reference.md
│   └── cli_usage.md
│
├── configs/                       # ⚙️ System Configs
│   ├── dev.yaml
│   ├── staging.yaml
│   ├── prod.yaml
│   ├── pipelines.yaml
│   ├── registry.yaml
│   ├── monitoring.yaml
│   └── logging.yaml
│
├── infra/                         # ☁️ Infrastructure
│   ├── docker/
│   │   ├── backend.Dockerfile
│   │   ├── frontend.Dockerfile
│   │   ├── worker.Dockerfile
│   │   └── cli.Dockerfile
│   │
│   ├── kubernetes/
│   │   ├── deployments/
│   │   ├── services/
│   │   ├── ingress/
│   │   └── helm-chart/
│   │
│   ├── terraform/
│   │   ├── aws/
│   │   ├── gcp/
│   │   └── azure/
│   │
│   └── monitoring/
│       ├── prometheus.yml
│       ├── grafana/
│       └── alertmanager.yml
│
├── backend/                       # 🧠 Core Backend (FastAPI)
│   ├── app/
│   │   ├── main.py
│   │   ├── api/
│   │   │   ├── routes/
│   │   │   │   ├── dashboard.py
│   │   │   │   ├── pipelines.py
│   │   │   │   ├── registry.py
│   │   │   │   ├── monitoring.py
│   │   │   │   ├── data_explorer.py
│   │   │   │   └── artifacts.py     # 📦 Artifact APIs
│   │   │   └── router.py
│   │   │
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   ├── security.py
│   │   │   ├── logging.py
│   │   │   └── exceptions.py
│   │   │
│   │   ├── services/
│   │   │   ├── dashboard_service.py
│   │   │   ├── pipeline_service.py
│   │   │   ├── registry_service.py
│   │   │   ├── monitoring_service.py
│   │   │   ├── data_profiling_service.py
│   │   │   └── artifact_service.py   # 📦 CORE ARTIFACT LOGIC
│   │   │
│   │   ├── db/
│   │   │   ├── models/
│   │   │   │   ├── pipeline.py
│   │   │   │   ├── model_registry.py
│   │   │   │   ├── dataset.py
│   │   │   │   ├── artifact.py       # 📦 artifact metadata
│   │   │   │   └── logs.py
│   │   │   ├── session.py
│   │   │   └── migrations/
│   │   │
│   │   ├── workers/
│   │   │   ├── celery_app.py
│   │   │   ├── pipeline_worker.py
│   │   │   ├── training_worker.py
│   │   │   └── artifact_worker.py    # 📦 async artifact processing
│   │   │
│   │   ├── ml/
│   │   │   ├── training/
│   │   │   ├── evaluation/
│   │   │   ├── feature_store/
│   │   │   └── drift_detection/
│   │   │
│   │   └── utils/
│   │       ├── file_io.py
│   │       ├── serializers.py
│   │       └── helpers.py
│
├── frontend/                      # 🖥️ Web UI (Next.js)
│   ├── public/
│   ├── src/
│   │   ├── app/
│   │   │   ├── dashboard/
│   │   │   ├── pipelines/
│   │   │   ├── data-explorer/
│   │   │   ├── registry/
│   │   │   ├── monitoring/
│   │   │   └── artifacts/        # 📦 Artifact viewer UI
│   │   │
│   │   ├── components/
│   │   │   ├── layout/
│   │   │   ├── charts/
│   │   │   ├── tables/
│   │   │   └── widgets/
│   │   │
│   │   ├── services/
│   │   │   ├── api.ts
│   │   │   ├── pipelines.ts
│   │   │   ├── registry.ts
│   │   │   ├── monitoring.ts
│   │   │   └── artifacts.ts
│   │   │
│   │   ├── store/
│   │   ├── hooks/
│   │   ├── utils/
│   │   └── styles/
│   │
│   └── package.json
│
├── cli/                           # 💻 CLI Tool (khops CLI)
│   ├── khops/
│   │   ├── main.py
│   │   ├── commands/
│   │   │   ├── init.py
│   │   │   ├── pipeline.py
│   │   │   ├── deploy.py
│   │   │   ├── monitor.py
│   │   │   ├── data.py
│   │   │   └── artifact.py       # 📦 CLI artifact commands
│   │   │
│   │   ├── client.py
│   │   ├── config.py
│   │   └── utils.py
│   │
│   └── pyproject.toml
│
├── sdk/                           # 📦 Python SDK
│   ├── khops/
│   │   ├── client.py
│   │   ├── pipeline.py
│   │   ├── registry.py
│   │   ├── monitoring.py
│   │   ├── dataset.py
│   │   ├── artifact.py          # 📦 SDK artifact API
│   │   └── exceptions.py
│   │
│   └── setup.py
│
├── services/                      # 🔌 Microservices (scalable split)
│   ├── pipeline-engine/
│   ├── model-serving/
│   ├── data-profiling/
│   ├── registry-service/
│   ├── monitoring-service/
│   └── artifact-service/         # 📦 standalone artifact service (optional scale-out)
│
├── artifacts/                    # 📦 CORE ARTIFACT STORE (LOCAL DEV)
│   │
│   ├── pipelines/                # 🔁 pipeline run outputs
│   │   └── pipeline_id=/
│   │       └── run_id=/
│   │           ├── inputs/
│   │           ├── outputs/
│   │           ├── logs/
│   │           ├── metrics.json
│   │           └── metadata.json
│   │
│   ├── models/                   # 🧠 model binaries
│   │   └── model_name=/
│   │       └── version=/
│   │           ├── model.pkl
│   │           ├── config.yaml
│   │           ├── metrics.json
│   │           ├── signature.json
│   │           └── explainability/
│   │
│   ├── datasets/                 # 📂 dataset versions
│   │   └── dataset_id=/
│   │       └── version=/
│   │           ├── data.csv
│   │           ├── schema.json
│   │           └── profiling_report.html
│   │
│   ├── evaluations/              # 📊 evaluation outputs
│   │   └── model=/
│   │       └── version=/
│   │           ├── confusion_matrix.png
│   │           ├── roc_curve.png
│   │           └── report.json
│   │
│   ├── monitoring/               # 📡 drift + performance snapshots
│   │   └── model=/
│   │       ├── drift_logs.json
│   │       └── latency_history.json
│   │
│   └── tmp/                      # 🧹 staging/cache
│
├── experiments/                  # 🧪 research zone
│   ├── notebooks/
│   ├── training_runs/
│   └── benchmarks/
│
├── tests/                        # 🧪 full test suite
│   ├── unit/
│   ├── integration/
│   ├── e2e/
│   └── load/
│
├── scripts/                      # 🔧 automation scripts
│   ├── setup_env.sh
│   ├── run_local.sh
│   ├── seed_db.py
│   └── deploy.sh
│
└── .github/
    ├── workflows/
    │   ├── backend-ci.yml
    │   ├── frontend-ci.yml
    │   ├── cli-release.yml
    │   └── deploy.yml
    │
    └── ISSUE_TEMPLATE/
</pre>


---

## 💻 KHOps CLI Commands

### Core
* `khops init`
* `khops login`
* `khops version`
* `khops doctor`
* `khops config show`
* `khops config set <key> <value>`

### Pipelines (includes training/experiments)
* `khops pipeline list`
* `khops pipeline create <name>`
* `khops pipeline run <pipeline_id>`
* `khops pipeline status <run_id>`
* `khops pipeline logs <run_id>`
* `khops pipeline stop <run_id>`
* `khops pipeline retry <run_id>`
* `khops pipeline delete <pipeline_id>`

#### Training (as pipeline stage)
* `khops pipeline train <pipeline_id> --experiment <name>`
* `khops pipeline compare <run_id_1> <run_id_2>`
* `khops pipeline metrics <run_id>`

### Data Explorer
* `khops data upload <file.csv>`
* `khops data profile <dataset_id>`
* `khops data stats <dataset_id>`
* `khops data drift <dataset_id>`
* `khops data schema <dataset_id>`

### Model Registry
* `khops registry list`
* `khops registry register <model_path>`
* `khops registry versions <model_name>`
* `khops registry promote <model_name> --version <n> --stage <env>`
* `khops registry rollback <model_name> --version <n>`
* `khops registry info <model_name>`

### Artifacts
* `khops artifact list`
* `khops artifact get <artifact_id>`
* `khops artifact download <artifact_id>`
* `khops artifact upload <file>`
* `khops artifact pipeline <run_id>`
* `khops artifact model <model_name> --version <n>`
* `khops artifact dataset <dataset_id>`

### Monitoring
* `khops monitor status`
* `khops monitor models`
* `khops monitor drift <model_name>`
* `khops monitor latency <service>`
* `khops monitor alerts`
* `khops monitor logs <service>`

### Dashboard
* `khops dashboard`
* `khops dashboard summary`
* `khops dashboard live`

### Deployment
* `khops deploy model <model_name>`
* `khops deploy pipeline <pipeline_id>`
* `khops deploy rollback <deployment_id>`
* `khops deploy status`

### Security / Governance
* `khops auth whoami`
* `khops audit logs`
* `khops permissions list`

### Utilities
* `khops cleanup artifacts`
* `khops help`

---

## 🌐 KHOps API Routes (v1)

Base URL: `/api/v1`

### 📊 Dashboard
- GET `/dashboard/summary`
- GET `/dashboard/system-health`
- GET `/dashboard/metrics/overview`
- GET `/dashboard/alerts`
- GET `/dashboard/activity-feed`

### 🔁 Pipelines (includes training)
- GET `/pipelines`
- POST `/pipelines`
- GET `/pipelines/{pipeline_id}`
- DELETE `/pipelines/{pipeline_id}`

#### Pipeline Runs
- POST `/pipelines/{pipeline_id}/run`
- GET `/pipelines/runs`
- GET `/pipelines/runs/{run_id}`
- GET `/pipelines/runs/{run_id}/logs`
- POST `/pipelines/runs/{run_id}/stop`
- POST `/pipelines/runs/{run_id}/retry`

#### Training (as pipeline stage)
- POST `/pipelines/{pipeline_id}/train`
- GET `/pipelines/runs/{run_id}/metrics`
- POST `/pipelines/compare`

### 📂 Data Explorer
- POST `/data/upload`
- GET `/data/datasets`
- GET `/data/datasets/{dataset_id}`
- GET `/data/datasets/{dataset_id}/schema`
- GET `/data/datasets/{dataset_id}/profile`
- GET `/data/datasets/{dataset_id}/stats`
- GET `/data/datasets/{dataset_id}/drift`

### 🧾 Model Registry
- GET `/registry/models`
- POST `/registry/models/register`
- GET `/registry/models/{model_name}`
- GET `/registry/models/{model_name}/versions`
- GET `/registry/models/{model_name}/versions/{version}`
- POST `/registry/models/{model_name}/promote`
- POST `/registry/models/{model_name}/rollback`

### 📦 Artifacts
- GET `/artifacts`
- GET `/artifacts/{artifact_id}`
- POST `/artifacts/upload`
- GET `/artifacts/download/{artifact_id}`
- GET `/artifacts/pipelines/{run_id}`
- GET `/artifacts/models/{model_name}/{version}`
- GET `/artifacts/datasets/{dataset_id}`

### 📡 Monitoring
- GET `/monitoring/status`
- GET `/monitoring/system`
- GET `/monitoring/models`
- GET `/monitoring/metrics/latency`
- GET `/monitoring/metrics/throughput`
- GET `/monitoring/drift/{model_name}`
- GET `/monitoring/alerts`
- GET `/monitoring/logs/{service}`

### 🚀 Deployment
- POST `/deploy/models/{model_name}`
- POST `/deploy/pipelines/{pipeline_id}`
- GET `/deploy/status`
- POST `/deploy/rollback/{deployment_id}`
- GET `/deploy/history`

### 🔐 Auth / Security
- POST `/auth/login`
- POST `/auth/logout`
- GET `/auth/me`
- POST `/auth/refresh`

### 🧑‍⚖️ Governance / Audit
- GET `/audit/logs`
- GET `/audit/logs/{entity_type}/{entity_id}`
- GET `/permissions`
- POST `/permissions/grant`
- POST `/permissions/revoke`

### 🧰 Utilities
- GET `/health`
- GET `/version`
- POST `/cleanup/artifacts`
- POST `/diagnostics/run`
