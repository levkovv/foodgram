#!/bin/sh
python3 manage.py migrate
python3 manage.py collectstatic --noinput
gunicorn foodgram_api.wsgi:application --bind 0:8000