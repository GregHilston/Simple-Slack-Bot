PYTHON=python3
.DEFAULT_GOAL := help
SHELL := /bin/bash
IMAGE_NAME=simple_slack_bot_dice_example

.PHONY: help
help: ## This help.
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

build: ## Builds the Dockerfile into an image.
	docker build -t ${IMAGE_NAME} .

run: ## Runs the Docker image as a container.
ifndef SLACK_BOT_TOKEN
	echo "required environment variable 'SLACK_BOT_TOKEN' is not defined"
	exit 1
endif
	docker run --env SLACK_BOT_TOKEN=${SLACK_BOT_TOKEN} -d ${IMAGE_NAME}
