.PHONY: install test generate run serve docker lint

install:
	pip install -e ".[dev]"
	npm install
	npx playwright install --with-deps chromium

test:
	zyvor-qa test

generate:
	zyvor-qa generate --spec prompts/examples/vm-create.md

run:
	zyvor-qa run --source local

serve:
	zyvor-qa serve --port 8080

docker:
	docker build -f docker/Dockerfile -t zyvor-qa-agent .
	docker run --env-file .env zyvor-qa-agent

lint:
	ruff check orchestrator agents github
	npx tsc --noEmit
