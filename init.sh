#!/bin/bash
set -e

echo "Starting SSH ..."
service ssh start
touch /home/site/wwwroot/evidence

gunicorn --bind=0.0.0.0:8000 --timeout 600 zhishangCarRental.wsgi