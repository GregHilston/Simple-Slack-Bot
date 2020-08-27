# README

This bot will write lines by characters from the show "The Office". It is a Dockerized example of using Simple Slack Bot. To run simply build the Docker image and then run the container.

The-Office-Bot will look at every message sent to the channels that it is in, waiting for a mention of the name of a character in the show The Office, specifically the US version. Once received, The-Office-Bot will write back a random line that this character had throughout the show, including lines from deleted scenes.

The data for The Office Bot was found from [here](https://www.reddit.com/r/datasets/comments/6yt3og/every_line_from_every_episode_of_the_office_us/)

To do to this with one command simply run `$ make run`.

_Note: Make sure to have your environment variable SLACK_BOT_TOKEN set in the Host OS. This value is passed to the Docker container for authentication_

_Note: The bot will only reply to channels that it is in. Don't forget to invite your bot into channels of interest!_

_Note: Be sure to download the dataset locally so it can be added to the image_
