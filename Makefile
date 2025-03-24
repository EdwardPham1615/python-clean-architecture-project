 TAG :=$(or ${CI_COMMIT_TAG}, latest)
DOCKER_IMAGE := python-clean-architecture-be:${TAG}

build:
	docker build -t ${DOCKER_IMAGE} .
.PHONY: build

start:
	docker-compose up -d
.PHONY: start

stop:
	docker-compose down -v
.PHONY: stop

restart:
	docker-compose restart
.PHONY: restart

format:
	isort . && ruff format $(pwd)
.PHONY: format