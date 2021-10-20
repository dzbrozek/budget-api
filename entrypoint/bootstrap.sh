#!/bin/bash

set -o errexit
set -o nounset

echo "Waiting for PostgreSQL"
. /app/entrypoint/wait-postgres.sh

echo "Running migrations"

python manage.py migrate

echo "Loading fixtures"

python manage.py loaddata ../fixtures/*.json

echo "Bootstrapped app"
