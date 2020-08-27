PYTHON=python3
.DEFAULT_GOAL := help
SHELL := /bin/bash
IMAGE_NAME=simple_slack_bot_the_office_example

.PHONY: help
help: ## This help.
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

build: ## Builds the Dockerfile into an image.
	docker build -t ${IMAGE_NAME} .

download_dataset_locally: ## Downloads the dataset locally which is orginally from https://www.reddit.com/r/datasets/comments/6yt3og/every_line_from_every_episode_of_the_office_us/
	# leading dash ignores error 8 response from Google Sheets
	-wget --output-file="the_office_lines_scripts.csv" "https://docs.google.com/spreadsheets/d/18wS5AAwOh8QO95RwHLS95POmSNKA2jjzdt0phrxeAE0/export?format=csv&gid=1" -O "the_office_lines_scripts.csv"

run: ## Runs the Docker image as a container.
ifndef SLACK_BOT_TOKEN
	echo "required environment variable 'SLACK_BOT_TOKEN' is not defined"
	exit 1
endif
	docker run --env SLACK_BOT_TOKEN=${SLACK_BOT_TOKEN} -d ${IMAGE_NAME}
