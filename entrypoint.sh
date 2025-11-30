#!/bin/bash

# Wait for database to be ready
echo "Waiting for database..."
while ! pg_isready -h db -p 5432 -U admin; do
  sleep 1
done
echo "Database is ready!"

# Run migrations
echo "Running database migrations..."
flask db upgrade || echo "No migrations to run"

# Start the application
echo "Starting application..."
exec python app.py
