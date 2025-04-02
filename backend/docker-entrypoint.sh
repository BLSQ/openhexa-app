#!/bin/bash
set -e

command=$1
arguments=${*:2}
if [[ -z $arguments ]]; then
  arguments_debug="no arguments"
else
  arguments_debug="arguments ($arguments)"
fi

# echo "Running \"$command\" with $arguments_debug"

show_help() {
  echo """
  Available commands:

  start             : start django server using gunicorn
  makemigrations    : generate a django migration
  migrate           : run django migrations & load base fixtures necessary for the app to work
  makemessages      : generate django translations
  compilemessages   : compile django translations
  test              : launch django tests
  manage            : run django manage.py
  fixtures          : migrate, create superuser, load demo & live fixtures and reindex
  bash              : run bash
  coveraged-test    : launch django tests and show a coverage report

  Any arguments passed will be forwarded to the executed command
  """
}

case "$command" in
"wait-for-it")
  $command $arguments
  ;;
"start")
  wait-for-it ${DATABASE_HOST:-db}:${DATABASE_PORT:-5432}
  gunicorn config.wsgi:application --bind 0:8000 --workers=3
  ;;
"makemigrations")
  wait-for-it ${DATABASE_HOST:-db}:${DATABASE_PORT:-5432}
  python manage.py $command $arguments
  ;;
"migrate")
  wait-for-it ${DATABASE_HOST:-db}:${DATABASE_PORT:-5432}
  python manage.py migrate $arguments
  # Load the base fixtures (features, data types, etc.)
  python manage.py loaddata base.json
  ;;
"makemessages" | "compilemessages")
  python manage.py $command $arguments
  ;;
"test")
  wait-for-it ${DATABASE_HOST:-db}:${DATABASE_PORT:-5432}
  export DJANGO_SETTINGS_MODULE=config.settings.test
  python manage.py makemigrations --check
  python manage.py test $arguments
  ;;
"coveraged-test")
  wait-for-it ${DATABASE_HOST:-db}:${DATABASE_PORT:-5432}
  export DJANGO_SETTINGS_MODULE=config.settings.test
  python manage.py makemigrations --check
  coverage run manage.py test $arguments
  python manage.py makemigrations --check
  coverage run manage.py test $arguments
  coverage report --skip-empty --fail-under=80
  ;;
"manage")
  wait-for-it ${DATABASE_HOST:-db}:${DATABASE_PORT:-5432}
  python manage.py $arguments
  ;;
"fixtures")
  wait-for-it ${DATABASE_HOST:-db}:${DATABASE_PORT:-5432}
  export DJANGO_SUPERUSER_USERNAME=root@openhexa.org
  export DJANGO_SUPERUSER_PASSWORD=root
  export DJANGO_SUPERUSER_EMAIL=root@openhexa.org
  python manage.py migrate
  python manage.py createsuperuser --no-input || true
  python manage.py loaddata base.json
  python manage.py loaddata demo.json
  python manage.py loaddata live.json
  python manage.py datasource_index
  python manage.py prepare_datasets
  ;;
"python")
  python $arguments
  ;;
"bash")
  bash $arguments
  ;;
"help")
  show_help
  ;;
*)
  show_help
  ;;
esac
