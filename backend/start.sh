#!/bin/bash
set -e

# Debug: verify DATABASE_URL is available
if [ -z "$DATABASE_URL" ]; then
    echo "WARNING: DATABASE_URL is not set!"
else
    echo "DATABASE_URL is set (scheme: ${DATABASE_URL%%://*})"
fi

echo "Running database migrations..."
alembic upgrade head

echo "Starting uvicorn on port ${PORT:-8000}..."
exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}"
