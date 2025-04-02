#!/usr/bin/env bash

echo "Copy template of Env file"
cp .env.dist .env

echo "Build App docker image"
docker compose build

echo "Add fixtures"
docker compose run app fixtures

echo "Setup pre-commit"
pre-commit install