#!/bin/bash
sleep 5
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py runserver 0.0.0.0:8000