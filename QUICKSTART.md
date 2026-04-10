# Quick Start Guide

## 🚀 Getting Started

### Prerequisites
- Python 3.9+
- Docker & Docker Compose
- Git

### Installation

1. **Clone and navigate to the project:**
```bash
cd /workspaces/KHOps
```

2. **Create virtual environment:**
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. **Install dependencies:**
```bash
make install
```

4. **Copy environment configuration:**
```bash
cp .env.example .env
```

### Development Setup

**Start local services:**
```bash
make docker-up
```

**Start API server (in another terminal):**
```bash
make server
```

**Access the platform:**
- 🖥️ API Docs: http://localhost:8000/docs
- 🔍 Prometheus: http://localhost:9090
- 📊 Grafana: http://localhost:3000 (admin/admin)

### CLI Usage

**Start the CLI:**
```bash
khops
```

**Available commands:**
```bash
khops server          # Start API server
khops run <pipeline>  # Execute a pipeline
khops register <model>  # Register a model
```

### Running Tests

```bash
make test           # Run tests
make test-cov       # Run with coverage
make lint           # Run linting
make format         # Format code
```

### Project Structure

```
khops/
├── cli/             # CLI commands
├── core/            # Configuration & logging
├── db/              # Database & models
├── server/          # FastAPI backend
├── pipelines/       # DAG execution
├── registry/        # Model registry
├── sdk/             # Python SDK
└── storage/         # Data storage
```

### Key Features

✅ **Pipeline Orchestration** - Build ML workflows as DAGs
✅ **Model Registry** - Version and manage models
✅ **Experiment Tracking** - Log metrics and parameters
✅ **Observability** - Monitor performance and drift
✅ **API Server** - REST API for all operations
✅ **CLI Interface** - Developer-first experience

### Next Steps

1. Review the [README.md](../README.md) for architecture details
2. Check [example pipelines](./examples/pipelines/)
3. Explore API documentation at http://localhost:8000/docs
4. Run sample pipeline: `khops run examples/pipelines/sample_pipeline.yaml`

### Troubleshooting

**Port already in use:**
```bash
# Change ports in .env file
# Or kill process: lsof -i :8000
```

**Database connection issues:**
```bash
# Check PostgreSQL is running
docker ps | grep postgres

# Check logs
make docker-logs
```

**Module import errors:**
```bash
# Reinstall package
pip install -e ".[dev]"
```

### Contributing

See [CONTRIBUTING.md] for guidelines.

### Documentation

- [Architecture Overview](./docs/architecture.md) - Coming soon
- [API Reference](./docs/api.md) - Coming soon
- [CLI Guide](./docs/cli.md) - Coming soon

### Support

- 📧 Email: support@khops.local
- 🐛 Issues: GitHub Issues
- 💬 Discussions: GitHub Discussions
