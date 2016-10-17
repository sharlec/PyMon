#!/bin/bash
source shlib/compose
source shlib/checks

COMPOSE="docker-compose.yml"
DEVELOP=true
CREATED=false

if [[ -z "${ARCH}" ]];
  then arch;
fi

function develop(){
  if [ ! -f ${COMPOSE} ]; then
    echo "Starting development environment"
    developyml "${COMPOSE}"
    DEVELOP=true
    CREATED=true
  else
    echo "Restarting previous session"
    echo "Clean up if you switch between development/deployment"
    CREATED=false
  fi
  start "${COMPOSE}" "${DEVELOP}" "${CREATED}"
}

function deploy() {
  if [ ! -f ${COMPOSE} ]; then
    echo "Starting deployment environment"
    deployyml "${COMPOSE}"
    DEVELOP=false
    CREATED=true
  else
    echo "Restarting previous session"
    echo "Clean up if you switch between development/deployment"
    CREATED=false
  fi
  start "${COMPOSE}" "${DEVELOP}" "${CREATED}"
}

function build() {
  docker-compose build
}

function stop() {
  docker-compose stop
}

function clean() {
  docker-compose down -v
  rm "${COMPOSE}"
}

function usage(){
cat << EOM
  usage:

  develop       initialize service with a simple sqlitedb
  deploy        initialize service with a postgres db and a caddy server
  build         rebuild all docker images
  stop          stop the application
  clean         remove everything (invokes stop)

EOM
}

# DIR=caddytest
if [[ $DEBUG == "true" ]]; then
  echo "$@"
  eval "$@"
  exit 0
#  exec "$@"
elif [ $# -eq 1 ]; then
  case "$1" in
    "develop")  develop;;
    "deploy")   deploy;;
    "build")    build;;
    "stop")     stop;;
    "clean")    clean;;
    *) usage;;
  esac
else
  usage
fi
exit 0
