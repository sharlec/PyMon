#!/usr/bin/env bash

MONIT_ARGS=${MONIT_ARGS:-"-I"}

if [ ! -d "${MONIT_HOME}/monitrc.d" ]; then
	mkdir ${MONIT_HOME}/monitrc.d
  cat <<-EOF > ${MONIT_HOME}/monitrc.d/basic
  set daemon 60

  set httpd port 2812
    allow localhost
    allow test:test
EOF
fi

for i in "${MONIT_LOG}/monit.pid ${MONIT_LOG}/monit.state"
do
	if [ -e "$i" ]; then
		rm "$i"
	fi
done

trap 'kill -SIGTERM $PID' SIGTERM SIGINT
monit ${MONIT_ARGS} &
PID=$!
wait $PID
