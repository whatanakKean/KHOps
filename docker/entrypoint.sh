#!/bin/bash
set -e

# Run database migrations
echo "Running database migrations..."
alembic upgrade head

# Seed database if needed
if [ "$SEED_DATABASE" = "true" ]; then
    echo "Seeding database..."
    python scripts/seed_db.py
fi

# Start the application
exec "$@"
