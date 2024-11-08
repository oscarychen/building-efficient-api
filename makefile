SHELL := /bin/bash

#!make
ifneq (,$(wildcard ./.env))
    include .env
    export
endif

docker-build:
	docker-compose build --no-cache

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-clean:
	@docker stop $$(docker ps -aq) || true
	@docker rm $$(docker ps -aq) || true
	@docker volume rm $$(docker volume ls -q) || true
	@docker rmi $$(docker images -q) || true
	@docker network rm $$(docker network ls -q) || true
	@docker system prune -a --volumes || true

django-drf-populate:
	docker exec -it api-demo-django-drf python manage.py populate