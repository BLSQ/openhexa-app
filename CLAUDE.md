# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Common Development Commands

### Backend (Django)

-   **Run backend server**: `docker compose up` (with `docker network create openhexa` first)
-   **Run tests**: `docker compose run app test --settings=config.settings.test`
-   **Run specific test**: `docker compose run app test hexa.core.tests.CoreTest.test_ready_200 --settings=config.settings.test`
-   **Exclude external tests**: `docker compose run app test --exclude-tag=external --settings=config.settings.test`
-   **Run migrations**: `docker compose run app migrate`
-   **Create fixtures**: `docker compose run app fixtures`
-   **Lint code**: `pre-commit run --all` (uses ruff for Python)
-   **Extract translations**: `docker compose run app manage makemessages -l fr`
-   **Compile translations**: `docker compose run app manage compilemessages`

### Frontend (Next.js)

-   **Install dependencies**: `npm install` (from `/frontend` directory)
-   **Development server**: `npm run dev`
-   **Build production**: `npm run build`
-   **Run tests**: `npm run test` (Jest with watch mode)
-   **Lint code**: `npm run lint`
-   **Format code**: `npm run format`
-   **Generate GraphQL types**: `npm run codegen`
-   **Extract i18n strings**: `npm run i18n:extract`
-   **Validate translations**: `npm run i18n:validate`

### Docker Compose Profiles

-   **Backend only**: `docker compose up`
-   **With frontend**: `docker compose --profile frontend up`
-   **With pipelines**: `docker compose --profile pipelines up`
-   **With dataset worker**: `docker compose --profile dataset_worker up`

## Architecture Overview

### Backend (Django) Architecture

OpenHEXA uses a **modular Django architecture** with the following key components:

**Core Apps:**

-   `core/` - Base models, GraphQL infrastructure, search functionality
-   `user_management/` - Authentication, organizations, teams
-   `workspaces/` - Collaborative environments with role-based access
-   `pipelines/` - Data pipeline execution and scheduling
-   `datasets/` - Dataset management with versioning
-   `files/` - Multi-backend file storage (GCP, filesystem)
-   `catalog/` - Search and discovery system

**Connector Plugins:**

-   Plugin architecture for external integrations (DHIS2, S3, PostgreSQL, etc.)
-   Each connector follows `ConnectorAppConfig` pattern

**Key Patterns:**

-   **Permission-first**: All queries filtered by user permissions using `filter_for_user()` methods
-   **Workspace-centric**: All data assets belong to workspaces
-   **Soft delete**: Most models support soft deletion
-   **Full-text search**: PostgreSQL with trigram similarity and GIN indexes
-   **GraphQL API**: Uses Ariadne with modular schema definitions

**Authentication Model:**

-   Custom User model with email as username
-   Multi-level permissions: Organization → Workspace → Resource
-   Roles: OWNER, ADMIN, EDITOR, MEMBER, VIEWER
-   Pipeline run authentication for automated access

### Frontend (Next.js) Architecture

The frontend uses **domain-driven architecture** with TypeScript:

**Structure:**

-   `core/` - Shared components, hooks, layouts
-   Domain modules: `datasets/`, `pipelines/`, `workspaces/`, etc.
-   Each domain has: `features/`, `graphql/`, `helpers/`, `hooks/`, `layouts/`

**Key Technologies:**

-   **Apollo Client** for GraphQL with sophisticated caching
-   **GraphQL Code Generator** for type-safe operations
-   **Server-side rendering** with Next.js
-   **Tailwind CSS** for styling
-   **React Context** for cross-cutting state
-   **Jest** for testing

**State Management:**

-   Apollo Client cache as primary state store
-   React Context for global state (user auth, layout)
-   Local hooks for component state

## Development Workflow

### Setting Up Environment

1. Copy `.env.dist` to `.env` and configure environment variables
2. Create Docker network: `docker network create openhexa`
3. Build and start services: `docker compose build && docker compose up`
4. Load fixtures: `docker compose run app fixtures`
5. Access at http://localhost:8000 (backend) and http://localhost:3000 (frontend)
6. Default login: `root@openhexa.org` / `root`

### Code Quality

-   **Python**: Uses `ruff` for linting, formatting, and import sorting (targets Python 3.13)
-   **JavaScript/TypeScript**: Uses `eslint` and `prettier` via Next.js
-   **Pre-commit hooks**: Automatically lint code before commits
-   **Conventional commits**: Required for automated releases
-   **Tests**: Comprehensive test suites for both backend and frontend

### GraphQL Development

-   Backend GraphQL schemas in `{app}/graphql/schema.graphql`
-   Frontend queries in `{domain}/graphql/*.graphql`
-   Run `npm run codegen` to regenerate TypeScript types
-   Schema combines all Django app schemas into unified API

### Database & Models

-   **PostgreSQL** with full-text search capabilities
-   **Base model pattern**: All models inherit from `Base` (UUID, timestamps)
-   **Permission filtering**: Always use `filter_for_user()` methods
-   **Migrations**: Standard Django migrations workflow
-   **Soft delete**: Use `objects` manager for active, `all_objects` for all records

### File Structure Conventions

-   **Backend**: Follow Django app structure with `models.py`, `schema.py`, `permissions.py`
-   **Frontend**: Domain-driven with consistent `features/`, `graphql/`, `hooks/` structure
-   **Tests**: Co-located with source code in `tests/` directories
-   **GraphQL**: Keep `.graphql` files next to their generated `.generated.tsx` counterparts

### Pipeline Development

-   Use OpenHEXA SDK for pipeline development
-   Configure SDK: `openhexa config set_url http://localhost:8000`
-   Pipelines support versioning, scheduling, and parameter passing
-   Container resources and timeouts configurable per pipeline

### Internationalization

-   **Backend**: Django i18n with message extraction and compilation
-   **Frontend**: i18next with automated extraction and DeepL translation
-   Supported languages: English (default), French
-   Translation files in `hexa/locale/` (backend) and `frontend/public/locales/` (frontend)
