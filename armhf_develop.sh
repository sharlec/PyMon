#!/bin/bash
orgdir=${PWD##*/}
dir=${orgdir//[-]/}
service=monitcollector
name=${dir}_${service}_1
yml=dc-develop-armhf.yml

docker-compose -f ${yml} up -d
sleep 2
echo "Setting up ${name}"

docker exec -it ${name} python manage.py createsuperuser --username "admin" --email "admin@example.com"

ln -sf ${yml} docker-compose.yml

echo "To stop the container again execute"
echo "docker-compose down -v"
