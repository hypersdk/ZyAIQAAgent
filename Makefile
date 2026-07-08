.PHONY: install test generate run serve docker lint regression create rust

install:
	pip install -e ".[dev]"
	npm install
	npx playwright install --with-deps chromium

test:
	zyvor-qa test

generate:
	zyvor-qa generate --spec prompts/examples/vm-create.md

create:
	zyvor-qa create "Verify homepage loads and shows product suite"

run:
	zyvor-qa run --source local

regression:
	ENABLE_REGRESSION=true zyvor-qa regression

regression-update:
	ENABLE_REGRESSION=true zyvor-qa regression --update-baselines

serve:
	zyvor-qa serve --port 8080

rust:
	cd rust && cargo build --release

docker:
	docker build -f docker/Dockerfile -t zyvor-qa-agent .
	docker run --env-file .env zyvor-qa-agent

lint:
	ruff check orchestrator agents github
	npx tsc --noEmit

k8s-apply:
	kubectl apply -f kubernetes/configmap.yaml -f kubernetes/secret.yaml -f kubernetes/deployment.yaml -f kubernetes/service.yaml -f kubernetes/cronjob.yaml
