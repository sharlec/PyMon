#!/bin/bash
orgdir=${PWD##*/}
dir=${orgdir//[-]/}
service=monitcollector
name=${dir}_${service}_1
yml=dc-deploy.yml

echo "Starting DB"
docker-compose -f ${yml} up -d db
sleep 5
echo "Setting up ${name}"
docker-compose -f ${yml} up -d
sleep 5
echo "Setting up Admin account"
docker exec -it ${name} python manage.py createsuperuser --username "admin" --email "admin@example.com"

ln -sf ${yml} docker-compose.yml

echo "To stop the container again execute"
echo "docker-compose down -v"
