#!/bin/bash
set -e

command=$1
arguments=$(echo "${*:2}" | xargs)
if [[ -z $arguments ]]; then
  arguments_debug="no argument"
else
  arguments_debug="arguments: $arguments"
fi

echo "Running \"$command\" ($arguments_debug)"

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
"wait-for-it" | "coverage")
  # shellcheck disable=SC2086
  $command $arguments
  ;;
"start")
  gunicorn config.wsgi:application --bind 0:8000 --workers=3
  ;;
"makemigrations" | "migrate" | "test")
  # shellcheck disable=SC2086
  python manage.py $command $arguments
  ;;
"manage")
  # shellcheck disable=SC2086
  python manage.py $arguments
  ;;
"bash")
  bash
  ;;
*)
  show_help
  ;;
esac
