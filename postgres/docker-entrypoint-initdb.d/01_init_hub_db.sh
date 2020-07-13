#!/bin/bash
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE DATABASE jupyterhub;
    GRANT ALL PRIVILEGES ON DATABASE jupyterhub TO postgres;
EOSQL

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE DATABASE habari_dev;
    GRANT ALL PRIVILEGES ON DATABASE habari_dev TO postgres;
EOSQL