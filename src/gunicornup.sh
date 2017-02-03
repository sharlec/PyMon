#!/bin/sh
# This file is used inside a container
WORKDIR=/usr/src/app
APP="monitcollector"

if [ ! -z "$DECOUPLE_DB" ]; then
  sed "s|.*DATABASE_URL.*|DATABASE_URL=$DECOUPLE_DB|g" ${WORKDIR}/env > ${WORKDIR}/.env
else
	cp ${WORKDIR}/env ${WORKDIR}/.env
fi

python3 manage.py migrate
python3 manage.py collectstatic --noinput

mkdir -p /var/www/env_projects/pymonit

if [ ! -f "/.created" ]; then
current=$PWD
tmp_file=admin.py
cd ${WORKDIR}
admin_user=${ADMIN:-admin}
echo ">>> >>> Setting up AdminUser ${admin_user}"
cat > ${tmp_file} <<-EOM
from django.contrib.auth.models import User;
User.objects.create_superuser('${admin_user}', '${EMAIL:-}', '${ADMIN_PWD:-1234}')
EOM

cat ${tmp_file} | python3 manage.py shell
rm ${tmp_file}
touch "/.created"
cd "${current}"
fi



# Prepare log files and start outputting logs to stdout
touch /usr/src/logs/gunicorn.log
touch /usr/src/logs/access.log
tail -n 0 -f /usr/src/logs/*.log &

if [ -f "$CERT/cert.pem" ] && [ -f "$CERT/key.pem" ]; then

	# Start Gunicorn processes
	echo Starting HTTPS Gunicorn.
	exec gunicorn wsgi:application \
		--name ${APP} \
		--bind 0.0.0.0:$LISTEN_PORT \
		--workers 3 \
		--keyfile $CERT/key.pem \
		--certfile $CERT/cert.pem \
		--ssl-version 3 \
		--do-handshake-on-connect \
		--log-level=info \
		--log-file=/usr/src/logs/gunicorn.log \
		--access-logfile=/usr/src/logs/access.log \
		"$@"
else
	echo Starting HTTP Gunicorn.

	exec gunicorn wsgi:application \
		--name ${APP} \
		--bind 0.0.0.0:$LISTEN_PORT \
		--workers 3 \
		--log-level=info \
		--log-file=/usr/src/logs/gunicorn.log \
		--access-logfile=/usr/src/logs/access.log \
		"$@"
fi
