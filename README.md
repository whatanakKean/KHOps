# 🌌 KHOps: High-Performance MLOps Platform

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python: 3.9+](https://img.shields.io/badge/Python-3.9+-darkgreen.svg)](https://www.python.org/)
[![UI: Synthetix Dark](https://img.shields.io/badge/UI-Synthetix_Dark-blueviolet.svg)](#design-principles)

**KHOps** is an open-source platform designed to streamline the entire machine learning lifecycle, from development to deployment and monitoring.

---

## 🚀 Key Objectives

-   **Automate Workflows:** Zero-friction orchestration from ingestion to deployment.
-   **Ensure Governance:** Full-lineage versioning and compliance for models and data.
-   **Enable Observability:** Deep-dive insights into P95 latency, model drift (KS metrics), and health.
-   **Streamline Deployment:** Rapid transition from experimental notebooks to production-ready APIs.

---

## 🛠 Core Functionality

### 1. KHOps Architect (Landing & Onboarding)
A high-conversion entry point highlighting the **Data Mesh** architecture and low-latency inference capabilities.

### 2. Executive Overview
A stakeholder-centric dashboard for real-time monitoring:
* Active Pipeline tracking & GPU/CPU utilization.
* Mean accuracy trends and compute cost analysis.
* Live deployment logs.

### 3. Visual Pipeline Designer
A drag-and-drop canvas for building complex ML DAGs:
* **Node Library:** Pre-built blocks for Data Ops, Training, and Evaluation.
* **Live Status:** Real-time visual feedback on node execution.

### 4. Model Registry & Observability
The brain of the platform:
* **Registry:** Searchable catalog with Staging/Production version control.
* **Observability:** Inference volume tracking, KS-test drift analysis, and error event streams.

---

## 🏗 Project Structure

```text
khops/
├── cli/             # Command-line interface & local entry points
├── core/            # Config, logging, and global constants
├── server/          # FastAPI backend (Routes, Services, Schemas)
├── pipelines/       # DAG Executor, Nodes, and Scheduler logic
├── registry/        # Model versioning and artifact storage manager
├── observability/   # Metrics collection, drift detection, and alerts
├── db/              # SQLAlchemy models and migrations
├── sdk/             # Client-side library for experiment tracking
└── web/             # Next.js/React frontend (Synthetix Dark UI)

---

## 🚀 Quick Start

1. Install dependencies:
   ```bash
   pip install -e ".[dev]"
   ```

2. Start the main API server:
   ```bash
   make server
   ```

3. Start the dedicated model serving API:
   ```bash
   make model-server
   ```

4. Run a pipeline from CLI:
   ```bash
   python -m khops.cli.main run examples/pipelines/sample_pipeline.yaml
   ```

5. Use the model serving route once a model is registered:
   - `POST http://localhost:8001/api/v1/serve/{model_name}`
   - Body format:
     ```json
     {
       "features": [
         {"feature1": 1.0, "feature2": 2.0}
       ]
     }
     ```

6. Launch the full CLI help menu:
   ```bash
   python -m khops.cli.main --help
   ```
