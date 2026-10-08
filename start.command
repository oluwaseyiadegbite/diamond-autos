#!/bin/bash
cd "$(dirname "$0")"
source venv/bin/activate
open http://127.0.0.1:8000
python manage.py runserver
