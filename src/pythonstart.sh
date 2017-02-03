#!/bin/sh
# This file is used inside a container
WORKDIR=/usr/src/app

cd ${WORKDIR}
cp env .env
python3 manage.py migrate
python3 manage.py collectstatic --noinput

if [ ! -f "/.created" ]; then
tmp_file=admin.py
cd ${WORKDIR}
echo ">>> >>> Setting up AdminUser ${admin_user}"
cat > ${tmp_file} <<-EOM
from django.contrib.auth.models import User;
User.objects.create_superuser('${ADMIN:-admin}','${EMAIL:-}', '${ADMIN_PWD:-1234}')
EOM

cat ${tmp_file} | python3 manage.py shell
rm ${tmp_file}
touch "/.created"
fi

python3 manage.py runserver 0.0.0.0:$LISTEN_PORT
