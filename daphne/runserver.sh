#!/bin/sh

# this is runserver using daphne
# activate virtual environment
source /opt/venv/bin/activate
# collect static files
python manage.py collectstatic --noinput
# runserver
daphne -b 0.0.0.0 -p 8000 core.asgi:application
