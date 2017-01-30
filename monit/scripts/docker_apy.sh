#!/bin/bash

echo $(curl -s ${DOCKER_SOCK});
exit $?;
