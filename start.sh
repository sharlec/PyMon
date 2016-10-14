#!/bin/bash
source shlib/compose
source shlib/checks

function develop(){
  baseyml
  echo "Not implemented yet"
}

function deploy() {
  echo "Not implemented yet"
}

function build() {
  echo "Not implemented yet"
}

function stop() {
  echo "Not implemented yet"
}

function usage(){
cat << EOM
  usage:

  develop       initialize service with a simple sqlitedb
  deploy        initialize service with a postgres db and a caddy server
  build         rebuild all docker images
  stop          stop the application

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
    "develop" )
      develop
      ;;
    "deploy" )
      deploy
      ;;
    "build" )
      build
      ;;
    "stop" )
      stop
      ;;
    * )
      usage
      ;;
  esac
else
  usage
fi
exit 0
