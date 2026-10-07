# Every target has a short alias and a long name; `make` or `make help` lists them.
# Backend/frontend counterparts share a letter and differ by a `b`/`f` suffix.
# Pass extra arguments to the underlying command with ARGS, e.g.
#   make tb ARGS="hexa.core.tests"
#   make tb ARGS="--exclude-tag=external"

.DEFAULT_GOAL := help

COMPOSE := docker compose
# Throwaway in-memory database in its own project, so it never touches the dev stack
COMPOSE_TEST := docker compose -p openhexa-test -f docker-compose.yaml -f docker-compose.test.yaml
NPM := npm --prefix frontend

.PHONY: help h \
	b build rb run_backend rbl run_backend_light rbsso run_backend_sso \
	tb tests_backend tbc tests_backend_coverage tbclean tests_backend_clean \
	lb lint_backend mk makemigrations m migrate fx fixtures db database s shell \
	if install_frontend rf run_frontend tf tests_frontend lf lint_frontend cg codegen i18n \
	t tests l lint

h help: ## Show this help
	@awk 'BEGIN { FS = ":.*## " } \
		/^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } \
		/^[a-zA-Z0-9_ -]+:.*## / { target = $$1; gsub(/ /, ", ", target); printf "  \033[36m%-32s\033[0m %s\n", target, $$2 }' $(MAKEFILE_LIST)
	@echo
	@echo 'Pass arguments to the underlying command with ARGS, e.g. make tb ARGS="hexa.core.tests"'

##@ Backend

b build: ## Build the backend docker image
	$(COMPOSE) build

rb run_backend: ## Run the backend with the pipelines and dataset workers
	$(COMPOSE) --profile pipelines --profile dataset_worker up

rbl run_backend_light: ## Run the backend without workers
	$(COMPOSE) up

rbsso run_backend_sso: ## Run the backend with the mock SSO provider
	$(COMPOSE) -f docker-compose.yaml -f docker-compose.oidc.yaml up

tb tests_backend: ## Run the backend tests against a throwaway in-memory database
	$(COMPOSE_TEST) run --rm app test $(ARGS)

tbc tests_backend_coverage: ## Run the backend tests with a coverage report
	$(COMPOSE_TEST) run --rm app coveraged-test $(ARGS)

tbclean tests_backend_clean: ## Remove the throwaway test database and its network
	$(COMPOSE_TEST) down

lb lint_backend: ## Lint the backend code (pre-commit)
	pre-commit run --show-diff-on-failure --color=always --all-files

mk makemigrations: ## Create migrations from model changes
	$(COMPOSE) run --rm app manage makemigrations $(ARGS)

m migrate: ## Apply migrations and load the base fixtures
	$(COMPOSE) run --rm app migrate $(ARGS)

fx fixtures: ## Load the demo fixtures
	$(COMPOSE) run --rm app fixtures

db database: ## Open a psql session on the dev database
	$(COMPOSE) exec db bash -c 'psql -U "$$POSTGRES_USER"'

s shell: ## Open a Django shell
	$(COMPOSE) run --rm app manage shell

##@ Frontend

if install_frontend: ## Install the frontend dependencies
	$(NPM) install

rf run_frontend: ## Run the frontend dev server
	$(NPM) run dev

tf tests_frontend: ## Run the frontend tests
	$(NPM) run test:ci

lf lint_frontend: ## Lint the frontend code
	$(NPM) run lint

cg codegen: ## Generate the GraphQL types
	$(NPM) run codegen

i18n: ## Extract the frontend translation strings
	$(NPM) run i18n:extract

##@ All

t tests: tests_backend tests_frontend ## Run the backend and frontend tests

l lint: lint_backend lint_frontend ## Lint the backend and frontend code
