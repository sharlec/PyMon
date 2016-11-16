#!/bin/sh
# This file is used inside a container
WORKDIR=/usr/src/app

cp ${WORKDIR}/env ${WORKDIR}/.env
cd ${WORKDIR}
python3 manage.py migrate
python3 manage.py collectstatic --noinput

if [ ! -f "/.created" ]; then
local current=$PWD
local tmp_file=admin.py
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

python3 manage.py runserver 0.0.0.0:$LISTEN_PORT
