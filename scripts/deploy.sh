#!/usr/bin/env bash
set -euo pipefail

if [ -f .env ]; then
  set -a
  source .env
  set +a
fi

echo "Building docker images..."
docker compose build

echo "Running database migrations..."
docker compose run --rm app python -c "import asyncio; from dsp.storage.repository import init_db; asyncio.run(init_db())"

echo "Seeding reference data (placeholder)..."
# TODO: add meaningful seed scripts here.

echo "Starting services..."
docker compose up -d

echo "Deployment completed."
