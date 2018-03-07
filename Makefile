DOCKER_COMPOSE := docker-compose -f
PRIMARY_GROUP := $(shell id -gn)
SUDO := sudo
ENVIRONMENT := development

.PHONY : run
run :  ## docker compose everything
	if [ ! -d "./database_data" ]; then mkdir -p ./database_data; fi
	@echo "environment: $(ENVIRONMENT)"
	@$(SUDO) chown -R $$USER:$(PRIMARY_GROUP) ./database_data; \
	$(DOCKER_COMPOSE) docker-compose.$(ENVIRONMENT).yml up -d

.PHONY : stop
stop : ## teardown compose containers
	@$(DOCKER_COMPOSE) docker-compose.$(ENVIRONMENT).yml stop; \
	$(DOCKER_COMPOSE) docker-compose.$(ENVIRONMENT).yml rm -f
