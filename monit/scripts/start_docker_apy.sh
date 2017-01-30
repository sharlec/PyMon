#!/bin/bash
${APY_HOME}/docker-sock.py &
echo $! > /var/run/py3_serve.pid
exit $?
