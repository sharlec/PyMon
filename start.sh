#!/bin/bash
source shlib/compose
source shlib/checks

ADMIN=${ADMIN:-admin}
PASSWD=${PASSWD:-1234}
EMAIL=${EMAIL:-"abc@example.com"}
REPO=${REPO:-"whatever4711"}
BUILD=${BUILD:-false}

COMPOSE="docker-compose.yml"
RYML="r-docker-compose.yml"
CREATED=false
TIMEOUT=10

check_dependencies
arch
evaluate_result $? " Detected architecture: ${ARCH}"

function develop() {
  if [ ! -f ${COMPOSE} ]; then
    info "Starting development environment"
    if [[ "$BUILD" == "true" ]]; then
      make architectures=${ARCH} src monit
    fi
    developyml "${COMPOSE}"
    CREATED=true
  else
    info "Restarting previous session"
    info "Clean up if you want to switch between development/deployment"
    CREATED=false
  fi
  start "${COMPOSE}" "${CREATED}"
}

function deploy() {
  if [ ! -f ${COMPOSE} ]; then
    info "Starting deployment environment"
    if [[ "$BUILD" == "true" ]]; then
      make architectures=${ARCH} src monit postgres caddy
    fi
    deployyml "${COMPOSE}"
    CREATED=true
  else
    info "Restarting previous session"
    info "Clean up if you want to switch between development/deployment"
    CREATED=false
  fi
  start "${COMPOSE}" "${CREATED}"
}

function build() {
  docker-compose build
}

function stop() {
  docker-compose stop
}

function clean() {
  if [ ! -f ${RYML} ]; then
    docker-compose -f "${COMPOSE}" down -v
  else
    docker-compose -f "${COMPOSE}" -f "${RYML}" down -v
  fi
  rm -f "${COMPOSE}" "${RYML}"
  sudo rm -rf src/__pycache__ src/monitcollector/__pycache__ src/monitcollector/migrations
}

function backup() {
  local orgdir="${PWD##*/}"
  local dir="${orgdir//[-]/}"
  mkdir -p backup

  # TODO For Postgres
  docker run --rm -v $PWD/backup:/backup -v ${dir}_pgdata:/data $(alpine) tar czf /backup/postgres.tar.gz data
  # TODO For SQLite
  docker run --rm -v $PWD/backup:/backup -v ${dir}_sqlitedb:/data $(alpine) tar czf /backup/sqlite.tar.gz data
  sudo chown -R $UID backup
}

function restore() {
  local orgdir="${PWD##*/}"
  local dir="${orgdir//[-]/}"
  # TODO container name
  docker run --rm -v $PWD/backup:/backup -v ${dir}_pgdata:/data alpine tar xzf /backup/data.tar.gz
}

function rplot() {
  ryml "${RYML}"
  plot "${COMPOSE}" "${RYML}"
}

function usage(){
cat << EOM
  usage:

  develop       initialize service with a simple sqlitedb
  deploy        initialize service with a postgres db and a caddy server
  stop          stop the application
  clean         remove everything (invokes stop)
  backup        create DB backup
  restore       restore backup
  rplot         generate R plots

EOM
}

if [ $# -eq 1 ]; then
  case "$1" in
    "develop")  develop;;
    "deploy")   deploy;;
    "stop")     stop;;
    "clean")    clean;;
    "backup")   backup;;
    "restore")  restore;;
    "rplot")    rplot;;
    *) usage;;
  esac
else
  usage
fi
exit 0
