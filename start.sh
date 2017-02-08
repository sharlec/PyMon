#!/bin/bash
source shlib/dockerfiles
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
    DEVELOP=true
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

function backup() {
  mkdir -p backup

  # TODO For Postgres
  docker run --rm -v $PWD/backup:/backup -v djangomonitcollector_pgdata:/data $(alpine) tar czf /backup/postgres.tar.gz data
  # TODO For SQLite
  docker run --rm -v $PWD/backup:/backup -v djangomonitcollector_sqlitedb:/data $(alpine) tar czf /backup/sqlite.tar.gz data
  sudo chown -R $UID backup
}

function restore() {
  # TODO container name
  docker run --rm -v $PWD/backup:/backup -v djangomonitcollector_pgdata:/data alpine tar xzf /backup/data.tar.gz
}

function usage(){
cat << EOM
  usage:

  develop       initialize service with a simple sqlitedb
  deploy        initialize service with a postgres db and a caddy server
  build         rebuild all docker images
  stop          stop the application
  clean         remove everything (invokes stop)
  backup        create DB backup
  restore       restore backup

EOM
}

if [ $# -eq 1 ]; then
  case "$1" in
    "develop")  develop;;
    "deploy")   deploy;;
    "build")    build;;
    "stop")     stop;;
    "clean")    clean;;
    "backup")     backup;;
    "restore")    restore;;
    *) usage;;
  esac
else
  usage
fi
exit 0
