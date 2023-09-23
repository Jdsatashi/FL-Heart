.PHONY: all

DOCKER_START = docker compose up -d --build
DOCKER_STOP = docker compose down

all: run restart

run:
	$(DOCKER_START)

restart:
	$(DOCKER_STOP) && $(DOCKER_START)