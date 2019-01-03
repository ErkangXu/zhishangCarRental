#!/bin/bash
set -e

echo "Starting SSH ..."
service ssh start

apt-get update
apt-get install g++
apt-get install unixodbc-dev

gunicorn --bind=0.0.0.0:8000 --timeout 600 ZhishangCarRental.wsgi