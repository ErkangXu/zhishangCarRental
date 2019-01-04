#!/bin/bash
set -e

echo "Starting SSH ..."
service ssh start

export DEBIAN_FRONTEND=noninteractive

apt-get install -my wget gnupg
apt-get install -y apt-transport-https

curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
curl https://packages.microsoft.com/config/debian/9/prod.list > /etc/apt/sources.list.d/mssql-release.list
apt-get update
sudo ACCEPT_EULA=Y apt-get -y install msodbcsql17
apt-get -y install g++
apt-get -y install unixodbc-dev

gunicorn --bind=0.0.0.0:8000 --timeout 600 ZhishangCarRental.wsgi