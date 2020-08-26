PYTHON=python3
.DEFAULT_GOAL := help
SHELL := /bin/bash

.PHONY: help
help: ## This help.
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

build: ## Builds the ping_pong example Dockerfile into an image.
	docker build -t simple_slack_bot_ping_pong_example .

run: build ## Runs the ping_pong Docker image as a container
	docker run --env SLACK_BOT_TOKEN=${SLACK_BOT_TOKEN} -d simple_slack_bot_ping_pong_example
