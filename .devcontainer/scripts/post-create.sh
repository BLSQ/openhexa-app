#!/bin/bash

# Create data directory
mkdir -p ./data

# Copy .env file
cp .env.dist .env

# Set workspace storage location
sed -i 's|WORKSPACE_STORAGE_LOCATION=.*|WORKSPACE_STORAGE_LOCATION=./data|' .env

# Create docker network
docker network create openhexa

# Start backend
docker compose build

