#!/bin/bash
set -e

echo "Starting SSH ..."
service ssh start

export DEBIAN_FRONTEND=noninteractive
apt-get update
apt-get -yp install g++
apt-get -yp install unixodbc-dev

gunicorn --bind=0.0.0.0:8000 --timeout 600 ZhishangCarRental.wsgi