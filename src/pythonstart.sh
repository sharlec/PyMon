#!/bin/bash
# This file is used inside a container
WORKDIR=/usr/src/app

cp ${WORKDIR}/env ${WORKDIR}/.env
cd ${WORKDIR}
python3 manage.py migrate
python3 manage.py collectstatic --noinput

python3 manage.py runserver 0.0.0.0:$LISTEN_PORT
