#!/usr/bin/env bash

json='{"timestamp":'$(date +%s)',"containers":'$(curl -s --unix-sock /var/run/docker.sock http::/containers/json)',"stats":[';
for id in $(curl -s --unix-sock /var/run/docker.sock http::/containers/json | jq -r ".[]|.Id"); do
        json="$json{\"id\":\"${id:0:12}\",\"stats\":$(curl -s --unix-sock /var/run/docker.sock http::/containers/$id/stats | head -n 1)},";
done;
echo "${json:0:-1}]}"
exit $?;

