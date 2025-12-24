#!/bin/bash
set -e
# Run migrations
echo "🔧 Running Alembic migrations..."
alembic upgrade head

# Start application
echo "Starting FastAPI application..."
uvicorn src.main:app --port 8000 --host 0.0.0.0 --reload
