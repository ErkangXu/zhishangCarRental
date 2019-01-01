#!/bin/bash
set -e

echo "Starting SSH ..."
service ssh start
touch /home/site/wwwroot/evidence

python manage.py runserver 0.0.0.0:8000