#!/bin/bash
source shlib/compose
source shlib/checks

ADMIN=${ADMIN:-admin}
PASSWD=${PASSWD:-1234}
EMAIL=${EMAIL:-"abc@example.com"}

COMPOSE="docker-compose.yml"
DEVELOP=true
CREATED=false
TIMEOUT=10

check_dependencies
arch
evaluate_result $? " Detected architecture: ${ARCH}"

function develop(){
  if [ ! -f ${COMPOSE} ]; then
    info "Starting development environment"
    developyml "${COMPOSE}"
    DEVELOP=true
    CREATED=true
  else
    info "Restarting previous session"
    info "Clean up if you want to switch between development/deployment"
    CREATED=false
  fi
  start "${COMPOSE}" "${DEVELOP}" "${CREATED}"
}

function deploy() {
  if [ ! -f ${COMPOSE} ]; then
    info "Starting deployment environment"
    deployyml "${COMPOSE}"
    DEVELOP=false
    CREATED=true
  else
    info "Restarting previous session"
    info "Clean up if you want to switch between development/deployment"
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
  rm -f "${COMPOSE}"
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

if [ $# -eq 1 ]; then
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
