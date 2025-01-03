#!/bin/bash

# Exit on any error
set -e

# Install dependencies
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --noinput

# Apply database migrations
python manage.py migrate

# Start Gunicorn
gunicorn core.wsgi:application --bind 0.0.0.0:$PORT --workers 4