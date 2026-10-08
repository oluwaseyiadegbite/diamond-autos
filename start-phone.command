#!/bin/bash
cd "$(dirname "$0")"
source venv/bin/activate
IP=$(ipconfig getifaddr en0)
export DJANGO_ALLOWED_HOSTS="localhost,127.0.0.1,$IP"
echo "On your phone (same Wi-Fi) open: http://$IP:8000"
python manage.py runserver 0.0.0.0:8000