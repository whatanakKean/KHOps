# 🎬 KHOps First-Time User Guide

**Welcome to KHOps!** 🚀

This guide will walk you through your first steps with the platform.

---

## Step 1: Verify Installation (2 minutes)

```bash
# Check that everything is installed correctly
cd /workspaces/KHOps

# 1. Verify CLI is accessible
khops --version
# Output: khops, version 0.1.0

# 2. List all CLI commands
khops --help
# Shows: server, run, register, config, logs, status, init

# 3. Verify Python package
python -c "import khops; print(khops.__version__)"
# Output: 0.1.0
```

---

## Step 2: Start Development Environment (3 minutes)

### Terminal 1: Start Docker Services
```bash
cd /workspaces/KHOps

# Start all services (PostgreSQL, Redis, Prometheus, Grafana, etc.)
make docker-up

# Wait for all containers to be healthy
# Output should show: ✅ All services started

# Check status
docker ps
# Should show 6 containers running
```

### Terminal 2: Start API Server
```bash
cd /workspaces/KHOps

# Start the FastAPI server with auto-reload
make server

# Output should show:
# 🚀 Starting KHOps Server (http://localhost:8000)
# Uvicorn running on http://0.0.0.0:8000
```

---

## Step 3: Access the Platform (1 minute)

Open your browser to these URLs:

### 🎨 API Documentation (Most Important!)
**http://localhost:8000/docs**
- Interactive Swagger UI
- Test all API endpoints
- See request/response schemas
- Explore all 25 endpoints

### Alternative Documentation
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI Spec**: http://localhost:8000/openapi.json

### 📊 Monitoring & Observability
- **Grafana**: http://localhost:3000 (admin/admin)
- **Prometheus**: http://localhost:9090
- **API Root**: http://localhost:8000

---

## Step 4: Test the API (5 minutes)

### Using Swagger UI (Recommended)
1. Go to http://localhost:8000/docs
2. Click on any endpoint (e.g., `GET /api/v1/health`)
3. Click "Try it out"
4. Click "Execute"
5. See the response below

### Using curl
```bash
# Health check
curl http://localhost:8000/api/v1/health
# Response: {"status":"healthy","timestamp":"...","version":"0.1.0"}

# List pipelines
curl http://localhost:8000/api/v1/pipelines
# Response: {"pipelines":[],"total":0,"status":"coming_soon"}

# List models
curl http://localhost:8000/api/v1/models
# Response: {"models":[],"total":0,"status":"coming_soon"}
```

### Using Python
```python
import requests

# Health check
response = requests.get("http://localhost:8000/api/v1/health")
print(response.json())

# List pipelines
response = requests.get("http://localhost:8000/api/v1/pipelines")
print(response.json())
```

---

## Step 5: Explore the CLI (3 minutes)

```bash
# View all available commands
khops --help

# Check system status
khops status
# Output: [*] Status check coming soon!

# Initialize a project (creates directories)
khops init
# Creates: pipelines/, models/, data/, scripts/

# View CLI logs
khops logs tail
# Shows: [*] Log viewing coming soon!
```

---

## Step 6: Explore the Codebase (10 minutes)

### Key Files to Review

```bash
# CLI Implementation
# Shows how commands are structured
cat khops/cli/main.py

# FastAPI Application
# Shows how the server is configured
cat khops/server/app.py

# Configuration Management
# Shows how settings are loaded
cat khops/core/config.py

# Health Route Example
# Shows how routes are implemented
cat khops/server/routes/health.py
```

### Project Structure
```
khops/
├── cli/main.py              ← Start here: CLI commands
├── server/app.py            ← FastAPI server
├── server/routes/           ← API endpoints
│   ├── health.py           ← Health checks
│   ├── metrics.py          ← Metrics endpoints
│   ├── models.py           ← Model registry
│   ├── pipelines.py        ← Pipeline management
│   └── runs.py             ← Run execution
├── core/
│   ├── config.py           ← Settings
│   └── logging.py          ← Logging setup
├── db/                      ← Database (TODO)
├── pipelines/               ← Pipeline execution (TODO)
├── registry/                ← Model registry (TODO)
└── storage/                 ← File storage (TODO)
```

---

## Step 7: Run Tests (3 minutes)

```bash
# Run quick tests
make test

# Run with coverage report
make test-cov
# Opens: htmlcov/index.html

# Run only unit tests
make test-unit

# Run linting
make lint

# Format code
make format
```

---

## Step 8: Understanding the Architecture

### API Structure
```
FastAPI App (khops/server/app.py)
├── Health Routes (3 endpoints)
├── Metrics Routes (3 endpoints)
├── Models Routes (5 endpoints)
├── Pipelines Routes (5 endpoints)
└── Runs Routes (4 endpoints)
```

### Data Flow
```
User/CLI
  ↓
FastAPI Server (port 8000)
  ↓
Routes (validate input)
  ↓
Services (business logic) - TODO
  ↓
Database Models (persistence) - TODO
  ↓
Docker Services (PostgreSQL, Redis, etc.)
```

### Technology Stack
- **Web Framework**: FastAPI
- **Server**: Uvicorn
- **ORM**: SQLAlchemy
- **Database**: PostgreSQL
- **Cache**: Redis
- **CLI**: Click
- **Monitoring**: Prometheus + Grafana
- **Logging**: Loki
- **Testing**: pytest

---

## Step 9: Common Tasks

### Adding a New API Endpoint

1. **Create route file** (if needed):
```python
# khops/server/routes/myroute.py
from fastapi import APIRouter

router = APIRouter()

@router.get("/myendpoint")
async def my_endpoint():
    return {"message": "hello"}
```

2. **Register in app.py**:
```python
from khops.server.routes import myroute
app.include_router(myroute.router, prefix="/api/v1", tags=["myroute"])
```

3. **Test in Swagger**: http://localhost:8000/docs

### Adding a CLI Command

1. **Edit khops/cli/main.py**:
```python
@cli.command()
@click.option("--name", required=True)
def mycommand(name: str):
    """My new command"""
    console.print(f"Hello {name}!")
```

2. **Test**: `khops mycommand --name World`

### Running Database Migrations

```bash
# Create migration
alembic revision --autogenerate -m "Add new table"

# Apply migration
make migrate

# Rollback
alembic downgrade -1
```

---

## Step 10: Troubleshooting

### Issue: Port 8000 already in use
```bash
# Find and kill the process
lsof -i :8000
kill -9 <PID>

# Or change port in .env
# CHANGE: SERVER_PORT=8000 TO SERVER_PORT=8001
```

### Issue: Docker services won't start
```bash
# Check what's running
docker ps -a

# View logs
make docker-logs

# Reset everything
make docker-down
make docker-clean
make docker-up
```

### Issue: Import errors
```bash
# Reinstall package
pip install -e ".[dev]" --force-reinstall --no-cache-dir
```

### Issue: Database connection failed
```bash
# Check PostgreSQL is running
docker ps | grep postgres

# Check credentials in .env
# Manual test: psql -U khops -h localhost -d khops -W
```

---

## Step 11: Next Steps - Implementation Roadmap

### This Week: Core Backend
- [ ] Implement database models
- [ ] Create services for each domain
- [ ] Add request/response schemas
- [ ] Write unit tests

### Next Week: Pipeline Execution
- [ ] Pipeline YAML parser
- [ ] DAG executor
- [ ] Node implementations
- [ ] Pipeline scheduler

### Week 3: Model Registry
- [ ] Model storage backend
- [ ] Versioning logic
- [ ] Stage management
- [ ] Model metadata

### Week 4: Observability
- [ ] Metrics collection
- [ ] Data drift detection
- [ ] Performance monitoring
- [ ] Alerting system

---

## Step 12: Quick Reference

### Useful Make Commands
```bash
make help              # Show all commands
make test              # Run tests
make lint              # Check code
make format            # Format code
make server            # Start API
make docker-up         # Start services
make docker-logs       # View logs
make clean             # Clean artifacts
```

### Useful URLs
```
API Docs:     http://localhost:8000/docs
API Root:     http://localhost:8000
Grafana:      http://localhost:3000
Prometheus:   http://localhost:9090
Database:     localhost:5432 (khops/khops_dev)
Redis:        localhost:6379
```

### Useful Files
```
Environment:  .env
Config:       khops/core/config.py
CLI Cmds:     khops/cli/main.py
API Server:   khops/server/app.py
Routes:       khops/server/routes/*.py
```

---

## 🎉 Congratulations!

You've successfully:
- ✅ Verified the installation
- ✅ Started the development environment
- ✅ Accessed the API documentation
- ✅ Tested the API endpoints
- ✅ Explored the CLI
- ✅ Reviewed the codebase
- ✅ Ran tests
- ✅ Understood the architecture

**You're now ready to start development!**

---

## 📚 Additional Resources

- **API Documentation**: http://localhost:8000/docs (interactive)
- **Project Overview**: `/workspaces/KHOps/README.md`
- **Quick Start**: `/workspaces/KHOps/QUICKSTART.md`
- **Full Setup Guide**: `/workspaces/KHOps/SETUP_COMPLETE.md`
- **Status Report**: `/workspaces/KHOps/PROJECT_STATUS.md`

---

## 💬 Getting Help

1. Check `/workspaces/KHOps/TROUBLESHOOTING.md` (if created)
2. Review API docs at http://localhost:8000/docs
3. Check logs: `make docker-logs`
4. Review code in `khops/server/routes/`
5. Run tests: `make test`

---

**Happy coding! 🚀**

Next: Implement the first feature by editing one of the service files!
