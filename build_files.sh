#!/bin/bash

# Install dependencies and override the managed environment block
python3 -m pip install -r requirements.txt --break-system-packages

# Collect static files
python3 manage.py collectstatic --noinput

# Run database migrations
python3 manage.py migrate --noinput