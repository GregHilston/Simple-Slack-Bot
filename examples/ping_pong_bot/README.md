# README

This bot will reply 'pong' to all 'ping' messages. It is a Dockerized example using Simple Slack Bot. To run simply build the Docker image and then run the container.

To do to this with one command simply run `$ make run`.

_Note: Make sure to have your environment variable SLACK_BOT_TOKEN set in the Host OS. This value is passed to the Docker container for authentication_

_Note: The bot will only reply to channels that it is in. Don't forget to invite your bot into channels of interest!_
