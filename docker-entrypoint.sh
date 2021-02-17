#!/bin/bash
set -e

command=$1
arguments=${*:2}
if [[ -z $arguments ]]; then
  arguments_debug="no arguments"
else
  arguments_debug="arguments ($arguments)"
fi

echo "Running \"$command\" with $arguments_debug"

show_help() {
  echo """
  Available commands:

  start            : start django server using gunicorn
  makemigrations   : generate a django migration
  migrate          : run django migrations
  test             : launch django tests
  manage           : run django manage.py
  bash             : run bash

  Any arguments passed will be forwarded to the executed command
  """
}

case "$command" in
"wait-for-it")
  $command $arguments
  ;;
"start")
  gunicorn config.wsgi:application --bind 0:8000 --workers=3
  ;;
"makemigrations" | "migrate")
  python manage.py $command $arguments
  ;;
"test")
  python manage.py test --parallel $arguments
  ;;
"coverage")
  coverage run --source='.' manage.py test
  coverage report
  ;;
"manage")
  python manage.py $arguments
  ;;
"fixtures")
  if [[ $DEBUG == "true" ]]; then
    export DJANGO_SUPERUSER_USERNAME=root
    export DJANGO_SUPERUSER_PASSWORD=root
    export DJANGO_SUPERUSER_EMAIL=root@bluesquarehub.com
    python manage.py migrate
    python manage.py createsuperuser --no-input || true
    python manage.py loaddata demo.json
  else
    echo "The \"fixtures\" command can only be executed in dev mode"
  fi
  ;;
"python")
  python $arguments
  ;;
"bash")
  bash $arguments
  ;;
*)
  show_help
  ;;
esac
