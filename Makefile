-include .env

DOCKER := docker
DOCKER_COMPOSE := docker-compose -f
PRIMARY_GROUP := $(shell id -gn)
SUDO := sudo
BASENAME := $(shell basename $(CURDIR))

.PHONY : run
run :  ## docker compose everything
	if [ ! -d "./database_data" ]; then mkdir -p ./database_data; fi
	@echo "environment: ${ENVIRONMENT}"
	@$(SUDO) chown -R $$USER:$(PRIMARY_GROUP) ./database_data; \
	$(DOCKER_COMPOSE) docker-compose.${ENVIRONMENT}.yml up -d

.PHONY : stop
stop : ## teardown compose containers
	@$(DOCKER_COMPOSE) docker-compose.${ENVIRONMENT}.yml stop; \
	$(DOCKER_COMPOSE) docker-compose.${ENVIRONMENT}.yml rm -f

.PHONY : reset_web
reset_web : ## teardown and recreate web container
	@$(DOCKER) stop $(BASENAME)_web_1; \
	$(DOCKER) rm $(BASENAME)_web_1; \
	$(DOCKER_COMPOSE) docker-compose.${ENVIRONMENT}.yml up -d

.PHONY : logs
logs : ## show logs from the last 10 minutes
	@echo Starting logs for $(BASENAME) ${ENVIRONMENT}...
	$(DOCKER) logs -f $(BASENAME)_web_1 --since 10m

.PHONY : db_localhost
db_localhost : ## change database to 127.0.0.1:3306 in .env
	@sed -i -e 's/@database/@127.0.0.1:3306/g' ./.env; \
  $(SOURCE_ENV)

.PHONY : db_unset_localhost
db_unset_localhost : ## change 127.0.0.1:3306 to database in .env
	@sed -i -e 's/@127.0.0.1:3306/@database/g' ./.env; \
  $(SOURCE_ENV)