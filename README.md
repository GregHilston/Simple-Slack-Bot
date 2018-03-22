# Simple Slack Bot

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

## Example

To integrate with Simple Slack Bot, simply create an instance of it and register for notifications using a Python decorator.

This can be seen with the following code below. Our Simple Slack Bot will reply to every message of "Ping", with "Pong", to every channel it's a part of:


`ping_pong.py`

```python

from simple_slack_bot import SimpleSlackBot

simple_slack_bot = SimpleSlackBot()

@simple_slack_bot.register("message")
def pong_callback(request):
    if request.message.lower() == "ping":
        request.write("Pong")


def main():
    simple_slack_bot.start()


if __name__ == "__main__":
    main()
```

At this point, your callback functions will be executed every time Simple Slack Bot receives the appropriate event.

A repo of this example Ping Pong Bot can be found [here](https://github.com/GregHilston/Ping-Pong-Bot). Feel free to use it as a refernec or fork it as a stating point!


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

If you have found that Simple Slack Bot does not provide everything you are looking for, you can gain access to the underlying [Slacker object](https://github.com/os/slacker) or [SlackSocket object](https://github.com/vektorlab/slacksocket) by calling


`get_slacker()`

or

`get_slack_socket()`

respectively on your instance of SimpleSlackBot


## Simple Slack Bots

We'll be maintaining a list of Simple Slack Bots here.

_If you have written a Simple Slack Bot, please contact me to have yours added!_


| Name                                                            | Author                                         | Description                                                                                                                                                                                                                                                                                                                                 |
|-----------------------------------------------------------------|------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| [Ping Pong Bot](https://github.com/GregHilston/Ping-Pong-Bot)   | [Greg Hilston](https://github.com/GregHilston) | Ping-Pong-Bot was created to act as an example of how easy it is to create a bot using the open source Simple-Slack-Bot library. Ping-Pong-Bot will look at every message sent to the channels that it is in, waiting for the case insensitive message "Ping". Once received Ping-Pong-Bot will write back to the very same channel "Pong". |
| [The Office Bot](https://github.com/GregHilston/The-Office-Bot) | [Greg Hilston](https://github.com/GregHilston) | The-Office-Bot will look at every message sent to the channels that,it is in, waiting for a mention of the name of a character in the show, The Office, specifically the US version. Once received, The-Office-Bot will write back a random line that this character had throughout the show, including lines from deleted scenes.          |
