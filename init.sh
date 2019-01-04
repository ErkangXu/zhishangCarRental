#!/bin/bash
set -e

echo "Starting SSH ..."
service ssh start

export DEBIAN_FRONTEND=noninteractive

apt-get -y install gnupg

curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
curl https://packages.microsoft.com/config/debian/9/prod.list > /etc/apt/sources.list.d/mssql-release.list
apt-get update
apt-get -y install msodbcsql17
apt-get -y install g++
apt-get -y install unixodbc-dev

gunicorn --bind=0.0.0.0:8000 --timeout 600 ZhishangCarRental.wsgi