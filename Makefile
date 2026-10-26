# Every target has a short alias and a long name; `make` or `make help` lists them.
# Backend/frontend counterparts share a letter and differ by a `b`/`f` suffix.
# Pass extra arguments to the underlying command with ARGS, e.g.
#   make tb ARGS="hexa.core.tests"
#   make tb ARGS="--exclude-tag=external"

.DEFAULT_GOAL := help

COMPOSE := docker compose
# Set in the .env of worktrees created by scripts/worktree.sh
PROJECT := $(shell sed -n 's/^COMPOSE_PROJECT_NAME=//p' .env 2>/dev/null)
# Throwaway in-memory database in its own project, so it never touches the dev stack
COMPOSE_TEST := docker compose -p $(or $(PROJECT),openhexa)-test -f docker-compose.yaml -f docker-compose.test.yaml
WORKTREE := scripts/worktree.sh
NPM := npm --prefix frontend

.PHONY: help h \
	b build rb run_backend rbl run_backend_light rbsso run_backend_sso \
	tb tests_backend tbc tests_backend_coverage tbclean tests_backend_clean \
	lb lint_backend mk makemigrations m migrate fx fixtures db database s shell \
	if install_frontend rf run_frontend tf tests_frontend lf lint_frontend cg codegen i18n \
	dev t tests l lint \
	worktree worktree-reset-db worktree-remove \
	e evals \

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

##@ Evals

# Spends real model tokens, unlike `make tests`. Start with DRY=1.
#   make e DRY=1                        check what would run, without calling the model
#   make e                              every case of the default suite
#   make e TASK=<task_id> REPEATS=1     one case, once
#   make e SUITE=<suite>                another suite
SUITE ?= pipeline_create

e evals: ## Run the agent evals (SUITE, TASK, REPEATS, DRY=1)
	$(COMPOSE) run --rm app manage run_evals --suite=$(SUITE) \
		$(if $(REPEATS),--repeats=$(REPEATS)) \
		$(if $(DRY),--dry-run) \
		$(foreach task,$(TASK),--task-id=$(task)) \
		$(ARGS) --settings=config.settings.eval

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

dev: ## Apply the migrations, run the backend in the background and the frontend
	$(COMPOSE) run --rm app migrate
	$(COMPOSE) up -d
	$(NPM) run dev

t tests: tests_backend tests_frontend ## Run the backend and frontend tests

l lint: lint_backend lint_frontend ## Lint the backend and frontend code

##@ Extra checkouts, to run several branches at once (see the README)

worktree: ## Create the next extra checkout (../openhexa-app-N) and open it in the IDE it is run from
	$(WORKTREE) new

worktree-reset-db: ## Reset an extra checkout's database from the main one (asks which, from the main checkout)
	$(WORKTREE) db

worktree-remove: ## Remove an extra checkout, its containers and database (asks which, from the main checkout)
	$(WORKTREE) remove
