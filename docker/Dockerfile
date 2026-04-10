FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    postgresql-client \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY pyproject.toml README.md LICENSE ./
COPY khops/ ./khops/
COPY scripts/ ./scripts/

# Install Python dependencies
RUN pip install --no-cache-dir -e .

# Create data directories
RUN mkdir -p /app/data/artifacts /app/data/models /app/data/registry /app/logs

# Expose port
EXPOSE 8000

# Default command
CMD ["uvicorn", "khops.server.app:app", "--host", "0.0.0.0", "--port", "8000"]
