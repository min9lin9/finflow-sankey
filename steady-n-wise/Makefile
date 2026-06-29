.PHONY: dev down test test-data test-backend test-frontend test-e2e compose-config

dev:
	docker compose up --build

down:
	docker compose down

compose-config:
	docker compose config

test: test-data test-backend test-frontend

test-data:
	cd data-service && uv run pytest

test-backend:
	cd backend && bun test

test-frontend:
	cd frontend && bun test

test-e2e:
	cd frontend && bunx playwright test
