# OpenHEXA Local Development Setup

## Overview

This document describes the local development environment setup for OpenHEXA, including custom port configurations and instructions for running the application.

## Architecture

OpenHEXA uses a monorepo structure with:
- **Backend**: Django application with GraphQL API
- **Frontend**: Next.js application with custom Express server
- **Database**: PostgreSQL with PostGIS extensions
- **Pipeline Services**: Scheduler and runner for data pipelines

## Port Configuration

The following ports have been configured to avoid conflicts with other applications:

| Service | Port | Notes |
|---------|------|-------|
| Backend (Django) | 8001 | Changed from default 8000 |
| Frontend (Next.js) | 3001 | Changed from default 3000 |
| Database (PostgreSQL) | 5434 | Exposed from container |
| MailHog Web UI | 8025 | Email testing interface |
| MailHog SMTP | 1025 | Email SMTP server |

### Port Modifications Made

1. **docker-compose.yaml** - Backend port mapping changed:
   ```yaml
   ports:
     - "8001:8000"  # Host:Container
   ```

2. **.env** - Backend URL and frontend port updated:
   ```bash
   OPENHEXA_BACKEND_URL=http://localhost:8001
   PORT=3001
   ```

3. **frontend/.env.local** - Frontend configuration:
   ```bash
   OPENHEXA_BACKEND_URL=http://localhost:8001
   PORT=3001
   ```

## Prerequisites

The following software is required:

- ✅ Docker Engine (v28.3.1 installed)
- ✅ Docker Compose (v2.38.1 installed)
- ✅ Node.js 20+ (v20.19.6 installed via nvm)
- ✅ nvm (Node Version Manager)

## Installation Steps Performed

### 1. Backend Setup

```bash
# Docker network was created
docker network create openhexa

# Environment file was copied
cp .env.dist .env

# Docker containers were built
docker compose build

# Database migrations and fixtures were loaded
docker compose run app fixtures
```

### 2. Node.js Upgrade

```bash
# Node.js 20 was installed for frontend compatibility
nvm install 20
nvm use 20
```

### 3. Frontend Setup

```bash
cd frontend

# Dependencies were installed
npm install

# Environment file was created
# See frontend/.env.local
```

## Running the Application

### Start Backend Services

From the project root directory:

```bash
# Start all backend services including pipelines
docker compose --profile pipelines up -d

# Check service status
docker compose ps

# View logs
docker compose logs -f app
```

**Backend endpoints:**
- GraphQL API: http://localhost:8001/graphql/
- Readiness check: http://localhost:8001/ready
- Admin panel: http://localhost:8001/admin/

### Start Frontend

From the `frontend` directory:

```bash
cd frontend

# Start development server with Node 20
bash -c 'source ~/.nvm/nvm.sh && nvm use 20 && npm run dev'
```

**Frontend URL:**
- Application: http://localhost:3001

### Default Login Credentials

- **Email**: root@openhexa.org
- **Password**: root

## Stopping Services

### Stop Backend

```bash
# Stop all backend services
docker compose --profile pipelines down

# Stop and remove volumes (⚠️ removes database data)
docker compose --profile pipelines down -v
```

### Stop Frontend

Press `Ctrl+C` in the terminal running the frontend, or:

```bash
# Kill the frontend process
pkill -f "node.*server/index.mjs"
```

## Development Workflow

### Backend Development

```bash
# Run tests
docker compose run app test --settings=config.settings.test

# Run specific test
docker compose run app test hexa.core.tests.CoreTest.test_ready_200 --settings=config.settings.test

# Run migrations
docker compose run app migrate

# Create superuser
docker compose run app createsuperuser

# Django shell
docker compose run app shell
```

### Frontend Development

```bash
cd frontend

# Run tests
npm run test

# Lint code
npm run lint

# Format code
npm run format

# Generate GraphQL types
npm run codegen

# Build for production
npm run build
```

## Troubleshooting

### Port Already in Use

If you see "port already in use" errors:

```bash
# Check what's using a port
lsof -i :8001  # or :3001

# Kill process on port
lsof -ti:8001 | xargs kill -9
```

### Frontend Won't Start

Ensure you're using Node.js 20+:

```bash
node --version  # Should be v20.19.6 or higher
nvm use 20      # Switch to Node 20
```

### Backend Database Connection Issues

```bash
# Check database container is running
docker compose ps db

# Check database logs
docker compose logs db

# Recreate database
docker compose down -v
docker compose up -d db
docker compose run app migrate
docker compose run app fixtures
```

### GraphQL Schema Issues

```bash
# Regenerate frontend GraphQL types
cd frontend
npm run codegen
```

## Additional Services

### MailHog (Email Testing)

MailHog captures all emails sent by the application during development:

- Web interface: http://localhost:8025
- SMTP server: localhost:1025

### Database Access

PostgreSQL is accessible at:

```bash
# Connection details
Host: localhost
Port: 5434
Database: hexa-app
Username: postgres
Password: postgres

# Connect via psql
psql -h localhost -p 5434 -U postgres -d hexa-app
```

## Notes

- The frontend uses a custom Express server that proxies certain requests (GraphQL, auth, files) to the backend
- Hot reloading is enabled for both frontend and backend in development mode
- The backend runs Django's development server inside Docker
- Pipeline services (scheduler and runner) are started with the `--profile pipelines` flag

## Quick Reference

```bash
# Start everything
docker compose --profile pipelines up -d
cd frontend && bash -c 'source ~/.nvm/nvm.sh && nvm use 20 && npm run dev'

# Stop everything
docker compose --profile pipelines down
pkill -f "node.*server/index.mjs"

# Access application
# Frontend: http://localhost:3001
# Backend: http://localhost:8001
# Login: root@openhexa.org / root
```
