#!/bin/sh
python ./manage.py migrate --no-input
python ./manage.py collectstatic --no-input

gunicorn bmat.wsgi:application \
    --bind 0.0.0.0:80 \
    --workers 1 \
    --timeout 90