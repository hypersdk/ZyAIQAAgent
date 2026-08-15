.PHONY: install test generate run serve docker lint regression create rust \
        k8s-check k8s-validate k8s-validate-cluster k8s-apply k8s-delete \
        desktop-dev desktop-build desktop-check

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

desktop-dev:
	cd desktop && npm install && npm run tauri dev

desktop-build:
	cd desktop && npm install && npm run tauri build

desktop-check:
	cd desktop && npm install && cd src-tauri && cargo check && cargo test

rust:
	cd rust && cargo build --release

docker:
	docker build -f docker/Dockerfile -t zyvor-qa-agent .
	docker run --env-file .env zyvor-qa-agent

lint:
	ruff check orchestrator agents github_integration
	npx tsc --noEmit

K8S_DIR := kubernetes

k8s-check:
	@kubectl cluster-info >/dev/null 2>&1 || { \
		echo "ERROR: No Kubernetes cluster is reachable."; \
		echo "  Start a local cluster (minikube, kind, Docker Desktop K8s) or set KUBECONFIG."; \
		echo "  To validate manifests without a cluster, run: make k8s-validate"; \
		exit 1; \
	}
	@echo "Kubernetes cluster is reachable."

k8s-validate:
	python3 scripts/validate_k8s_manifests.py

k8s-validate-cluster: k8s-check
	kubectl apply --dry-run=server -f $(K8S_DIR)/configmap.yaml -f $(K8S_DIR)/secret.yaml -f $(K8S_DIR)/rbac.yaml -f $(K8S_DIR)/pvc.yaml -f $(K8S_DIR)/deployment.yaml -f $(K8S_DIR)/service.yaml -f $(K8S_DIR)/cronjob.yaml

k8s-apply: k8s-check
	kubectl apply -f $(K8S_DIR)/configmap.yaml -f $(K8S_DIR)/secret.yaml -f $(K8S_DIR)/rbac.yaml -f $(K8S_DIR)/pvc.yaml -f $(K8S_DIR)/deployment.yaml -f $(K8S_DIR)/service.yaml -f $(K8S_DIR)/cronjob.yaml

k8s-delete: k8s-check
	kubectl delete -f $(K8S_DIR)/configmap.yaml -f $(K8S_DIR)/secret.yaml -f $(K8S_DIR)/rbac.yaml -f $(K8S_DIR)/pvc.yaml -f $(K8S_DIR)/deployment.yaml -f $(K8S_DIR)/service.yaml -f $(K8S_DIR)/cronjob.yaml --ignore-not-found
