#!/bin/sh
set -eo pipefail

host="$(hostname -i || echo '127.0.0.1')"
user="${POSTGRES_USER:-postgres}"
export PGPASSWORD="${POSTGRES_PASSWORD:-}"

if select="$(echo 'SELECT 1' | psql -h $host -U $user --quiet --no-align --tuples-only)" && [ "$select" = '1' ]; then
	exit 0
fi

exit 1
