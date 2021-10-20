#!/bin/bash

set -o errexit
set -o nounset

. /app/entrypoint/wait-postgres.sh

python manage.py migrate
python manage.py runserver 0.0.0.0:8000 "$@"
