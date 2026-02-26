r run:
	@echo "Running backend with pipelines and dataset workers"
	docker compose --profile pipelines --profile dataset_worker up

rl run_light:
	@echo "Running backend without workers"
	docker compose up

rf run_front:
	@echo "Running frontend"
	npm run dev --prefix frontend

t tests:
	@echo "Running tests"
	docker compose run -u $(id -u):$(id -g) app coveraged-test

lb lint_backend:
	@echo "Executing lint in backend code (pre-commit)"
	pre-commit run --show-diff-on-failure --color=always --all-files

lf lint_frontend:
	@echo "Executing lint in frontend code"
	npm run lint --prefix frontend

l lint:
	make lb
	make lf

mk makemigrations:
	@echo "Creating migrations"
	docker compose run app manage makemigrations

m migrate:
	@echo "Executing migrations"
	docker compose run app manage makemigrations
	docker compose run app manage migrate

db database:
	@echo "Accessing local db"
	docker exec -it openhexa-app-db-1 bash -c "psql -U hexa-app"

s shell:
	@echo "Accessing django shell"
	docker compose run app manage shell
