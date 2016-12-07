#!/bin/bash

NET='monit_net'
SHARE_HOST='cubietruck.mg'
SHARE_DIR='/home/marcel/clouddata/monit'
SHARE=${SHARE_HOST}:${SHARE_DIR}
VOLUMES=( 'monit_db' 'monit_www' )
declare -a SERVICES
filename=services.txt

ADMIN=${ADMIN:-admin}
PASSWD=${PASSWD:-1234}
EMAIL=${EMAIL:-"abc@example.com"}

# Requires su rights
function reset {
tmp=tmp
mkdir ${tmp}
mount ${SHARE} ${tmp}
cd ${tmp}
for volume in "${VOLUMES[@]}"; do
	echo "Removing contents of ${volume}"
	rm -rf ${volume}
	echo "Recreating ${volume}"
	mkdir ${volume}
done
cd ..
umount ${tmp}
rm -rf ${tmp}
}

function getServices {
	if [ -f ${filename} ]; then
	  mapfile -t SERVICES < ${filename}
	else
	  SERVICES=()
	fi
}

function setServices {
	echo ${SERVICES[@]} > ${filename}
}

function createBasics {
echo "Creating network ${NET}"
docker network create --driver overlay ${NET}
for volume in "${VOLUMES[@]}"; do
	echo "Creating volume ${volume}"
	docker volume create -d nfs --name ${volume} -o share=${SHARE}/${volume}
done
ssh cubietruck.mg "docker volume create -d nfs --name ${VOLUMES[0]} -o share=${SHARE}/${VOLUMES[0]}"
}

function createDB {
local db=${1:-monit_postgres}
echo "Creating DB service ${db} with volume ${VOLUMES[0]}"
docker service create --name ${db} --replicas 1 --network ${NET} \
  --env POSTGRES_DB=pymonit \
	--publish 5433:5432 \
	--mount type=volume,src=${VOLUMES[0]},dst=/var/lib/postgresql/data \
	--constraint 'node.hostname==cubietruck' \
	whatever4711/postgres:armhf
SERVICES+=("${db}")
}

function createCollector {
local collector=${1:-monit_collector}
echo "Creating Nextcloud service ${collector} with volume ${VOLUMES[1]}"
docker service create --name ${collector} --replicas 1 --network ${NET} \
	--publish 8000:8000 \
	--mount type=volume,src=${VOLUMES[2]},dst=/usr/src/app/static \
  --mount type=bind,src=${PWD}/src,dst=/usr/src/app \
  --env ADMIN=${ADMIN} \
  --env ADMIN_PWD=${PASSWD} \
  --env EMAIL=${EMAIL} \
	--env LISTEN_PORT=8000 \
	--env DECOUPLE_DB=postgresql://postgres:postgres@192.168.9.3:5433/pymonit \
	--constraint 'node.hostname==sparrow' \
	whatever4711/django-monit-collector:armhf
SERVICES+=("${collector}")
}

function create_ssh {
local ssh=${1:-monit_ssh}
echo "Creating SSH service ${ssh}"
docker service create --name ${ssh} --replicas 1 --network ${NET} \
	--publish 2223:22 \
	--env ROOT_PASS=12wert45 \
	--constraint 'node.hostname!=roupi' \
	whatever4711/ssh:armhf
SERVICE+=("${ssh}")
}


function create {
createBasics
sleep 10
createDB
setServices
}

function start {
getServices
createCollector
setServices
}

function debug {
getServices
create_ssh
setServices
}

function destroy {
getServices
for service in "${SERVICES[@]}"; do
	docker service rm ${service}
done
sleep 10

for volume in "${VOLUMES[@]}"; do
	docker volume rm ${volume}
done
sleep 10
docker network rm ${NET}
rm ${filename}
}



function usage(){
cat << EOM
usage:

create       create
start        start
debug        debugging with ssh container
destroy      destroy
reset        reset

EOM
}

if [ $# -eq 1 ]; then
	case "$1" in
		"create")  create;;
		"start")   start;;
		"debug")   debug;;
		"destroy")    destroy;;
		"reset")    reset;;
		*) usage;;
	esac
else
	usage
fi
exit 0
