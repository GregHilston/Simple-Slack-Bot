# Simple Slack Bot

[![<ORG_NAME>](https://circleci.com/gh/GregHilston/Simple-Slack-Bot.svg?style=svg)](https://app.circleci.com/pipelines/github/GregHilston/Simple-Slack-Bot) [![codecov](https://codecov.io/gh/GregHilston/Simple-Slack-Bot/branch/master/graph/badge.svg)](https://codecov.io/gh/GregHilston/Simple-Slack-Bot) [![PyPI version](https://badge.fury.io/py/simple-slack-bot.svg)](https://badge.fury.io/py/simple-slack-bot)


Simple Slack Bot makes writing your next Slack bot incredibly easy. By factoring out common functionality all Slack Bots require, you can focus on writing your business logic.


## Installing
### Pip
Run:

`$ pip3 install simple_slack_bot`

### From Source
To install, simply clone the source, which will allow you to import SimpleSlackBot.


## Configuration

To configure, set a single environment variable

`SLACK_BOT_TOKEN` with your Slack Bot's API token


### Finding Your Slack Bot API Token

To generate or locate your Slack Bot Token, visit

> https://[YOUR SLACK TEAM NAME HERE].slack.com/apps/manage/custom-integrations

and click

> Bots

If you already have a bot created, you should see it listed here, otherwise you should be able to click

> Add Configuration

to create one.

Once you have a bot find it listed in the configurations and click the

> Edit

icon. You'll be brought to a page that lists your API token. This is what you'll use with Simple Slack Bot.

## Example

To integrate with Simple Slack Bot, simply create an instance of it and register for notifications using a Python decorator.

This can be seen with the following code below. Our Simple Slack Bot will reply to every message of "Ping", with "Pong", to every channel it's a part of:


`ping_pong.py`

```python

from simple_slack_bot.simple_slack_bot import SimpleSlackBot

simple_slack_bot = SimpleSlackBot(debug=True)


@simple_slack_bot.register("message")
def pong_callback(request):
    if request.message and request.message.lower() == "ping":
        request.write("Pong")


def main():
    simple_slack_bot.start()


if __name__ == "__main__":
    main()

```

At this point, your callback functions will be executed every time Simple Slack Bot receives the appropriate event.

A repo of this example Ping Pong Bot can be found [here](https://github.com/GregHilston/Ping-Pong-Bot). Feel free to use it as a reference or fork it as a stating point!


### Debug Mode

Note: Simple Slack Bot can be initialized with debug mode turned on, which will display all debug messages out to stdout and stderr.

To enable this simply pass `debug=True` when initializing Simple Slack Bot. As seen below:

```python
simple_slack_bot = SimpleSlackBot(debug=True)
```


#### Additional Logging Control

If you want more control on the routing of your logging, instead of passing `debug=True` when initializing Simple Slack Bot, you can configure the global `logging` variable in your own application.

An example:

```
import logging
from simple_slack_bot.simple_slack_bot import SimpleSlackBot

dict_config = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
    },
    'handlers': {
        'default': {
            'level': 'INFO',
            'formatter': 'standard',
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        '': {
            'handlers': ['default'],
            'level': 'INFO',
            'propagate': True
        },
        'django.request': {
            'handlers': ['default'],
            'level': 'WARN',
            'propagate': False
        },
    }
}

simple_slack_bot = SimpleSlackBot()
logging.config.dictConfig(dict_config)
```

Where you'd create your own `dictConfig` based on your own needs.


## Supported Events

Simple Slack Bot handles all of the parsing and routing of Slack events. To be informed of new slack events, you must register a callback function with Simple Slack Bot for each event. All Slack Events are registered to and can be seen [here](https://api.slack.com/events/api).


## The `request` Object

Each method you decorate in your Simple Slack Bot will need to take in a `request`. The contents of the `request` will differ depending on the event(s) you register to.

For each event you register for, take a look at the event [here](https://api.slack.com/events/api), as this is where the contents of the request will be defined.

For convenience, I've added the following attributes to all `request` objects:

* `type` - type of event
* `channel` - the channel from the underlying SlackEvent
  - _Note: This can be an empty String. For example, this will be an empty String for the 'Hello' event._
* `message` - the received message


## Helper Functions & Callbacks Making Callbacks
Often times when writing a Slack Bot, you'll find yourself writing a few key functions that I found generic enough to include in Simple-Slack-Bot. The function names are pretty self explanatory but they are as follows:


* `helper_write(channel, content)` - Writes a message to the channel as the bot
* `helper_get_public_channel_ids()` - Gets all public channel ids
* `helper_get_private_channel_ids()` - Gets all private channel ids
* `helper_get_user_ids()` - Gets all user ids
* `helper_get_users_in_channel(channel_id)` - Gets all users in a given channel
* `helper_name_to_channel_id(name)` - Converts a channel name to its respected channel id
* `helper_user_name_to_user_id(name)` - Converts a user name to its respected user id
* `helper_channel_id_to_channel_name(channel_id)` - Converts a channel id to its respected channel name
* `helper_user_id_to_user_name(user_id)` - Converts a user id to its respected user name

To gain access to these functions, simply call the appropriate function on your SimpleSlackBot instance.


## Writing More Advanced Slack Bots

If you have found that Simple Slack Bot does not provide everything you are looking for, you can gain access to the underlying [python Slack Client](https://github.com/slackapi/python-slackclient) or [SlackSocket object](https://github.com/vektorlab/slacksocket).

## Running Local Development Version

If you want to run the local version of Simple Slack Bot and not the verison you downloaded through PyPi, you can run the following in the `Simple-Slack-Bot` directory:

`python3 setup.py install`

and then import it as usual

`from simple_slack_bot.simple_slack_bot import SimpleSlackBot`.

You'll also have to install Simple Slack Bot's dependencies using PyPi. A `requirements.txt` will be kept up to date, along side the `setup.py` for this use case and your convenience.


## Unit Tests

To run the unit test suite, execute

`$ make test`


To generate code coverage of the unit test suite, execute:

`$ make test-and-generate-coverage`

## Simple Slack Bots

We'll be maintaining a list of Simple Slack Bots here.

_If you have written a Simple Slack Bot, please contact me to have yours added!_


|                               Name                              |                        Author                        |                                                                                                                                                                 Description                                                                                                                                                                 |
|:---------------------------------------------------------------:|:----------------------------------------------------:|:-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------:|
| [Ping Pong Bot](https://github.com/GregHilston/Ping-Pong-Bot)   | [Greg Hilston](https://github.com/GregHilston)       | Ping Pong Bot was created to act as an example of how easy it is to create a bot using the open source Simple-Slack-Bot framework. Ping-Pong-Bot will look at every message sent to the channels that it is in, waiting for the case insensitive message "Ping". Once received Ping-Pong-Bot will write back to the very same channel "Pong". |
| [The Office Bot](https://github.com/GregHilston/The-Office-Bot) | [Greg Hilston](https://github.com/GregHilston)       | The Office Bot will look at every message sent to the channels that,it is in, waiting for a mention of the name of a character in the show, The Office, specifically the US version. Once received, The-Office-Bot will write back a random line that this character had throughout the show, including lines from deleted scenes.          |
| [Stan Bot](https://github.com/jahirfiquitiva/StanBot)           | [Jahir Fiquitiva](https://github.com/jahirfiquitiva) | Stan Bot is a bot to help one with the SCRUM stand-up process.                                                                                                                                                                                                                                                                              |
| [Dice Bot](https://github.com/GregHilston/dice_bot)             | [Greg Hilston](https://github.com/GregHilston)       | Dice Bot is used to perform simple dice rolls                                                                                                                                                                                                                                                                                               |
| [DnD Bot](https://github.com/GregHilston/D-And-D-Bot)             | [Greg Hilston](https://github.com/GregHilston)     | D and D Bot is used record small D&D sessions that take place in Slack, by recording the in gmae chat to a `csv`                                                                                                                                                                                                                            |
