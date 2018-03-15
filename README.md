# Simple Slack Bot

Simple Slack Bot makes writing your next Slack bot incredibly easy. By factoring out common functionality all Slack Bots require, you can focus on writing your business logic.


## Installing
### Pip
Run:

`$ pip3 install simple_slack_bot`

### From Source
To install, simply clone the source, which will allow you to import SimpleSlackBot.


## Configuration

To configure, set the two environment variables

`SLACK_BOT_TOKEN` with your Slack Bot's API token

## Example

To integrate with Simple Slack Bot, simply create an instance of it and register for notifications using a callback function. This can be accomplished using the following code:


`ping_pong.py`

```
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

At this point your callback functions will be executed every time Simple Slack Bot receives the appropriate event.


## Supported Events

Simple Slack Bot handles all of the parsing and routing of Slack events. To be informed of new slack events, you must register a callback function with Simple Slack Bot for each event. All Slack Events are registered to and can be seen [here](https://api.slack.com/events-api).


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

If you have found that Simple-Slack-Bot does not provide everything you are looking for, you can gain access to the underlying [Slacker object](https://github.com/os/slacker) or [SlackSocket object](https://github.com/vektorlab/slacksocket) by calling


`get_slacker()`

or

`get_slack_socket()`

respectively.
