# Simple Slack Bot

Simple Slack Bot makes writing you next basic Slack bot incredibly quickly. By factoring out common functionality all Slack Bots require, you can focus on writing your business logic.


## Installing
To install, simply clone the source, which will allow you to import SimpleSlackBot.


## Configuration

To configure, set the two environment variables

`SLACK_BOT_TOKEN` with your Slack Bot's API token

`BOT_ID` with the Slack ID of your bot.
*Note: This is the String representation*


## Registering For Events

Simple Slack Bot handles all of the parsing and routing of Slack events. To be informed of new slack events, you must register a callback function with Simple Slack Bot for each event. The following events can be registered to:

* `register_hello(call_back)` - Registers the callback for the "Hello" event, which Slack sends upon logging in. For more information about the hello event and details on the format of the JSON return object see https://api.slack.com/events/hello


* `register_mentions(callback)` - Registers the callback for "Mention" events, which Slack sends upon users mentioning your bot via its `BOT_ID` like this `@BOT_ID This is a mention!`. For details on the format of the JSON return object see https://api.slack.com/events/message

* `register_public_channels_message(callback)` - Registers the callback for "Message" events that occur in all public channels the bot is in.  Again, for more information about the message event and details on the format of the JSON return object see https://api.slack.com/events/message

* `register_private_channels_message(callback)` - Registers the callback for "Message" events that occur in all private channels the bot is in.  Again, for more information about the message event and details on the format of the JSON return object see https://api.slack.com/events/message

* `register_direct_messages(callback)` - Registers the callback for "Message" events that occur in a direct message. For details on the format of the JSON return object see https://api.slack.com/events/message

*Note: In addition to the links provided, feel free to visit Slack's api here "https://api.slack.com/"*


## Integrating

To integrate with Simple Slack Bot, simply create an instance of it and register for notifications using a callback function. This can be accomplished using the following code:


`app.py`

```
from simple_slack_bot import SimpleSlackBot


def main():
    simple_slack_bot = SimpleSlackBot()
    # register with simple_slack_bot here
    simple_slack_bot.start()


if __name__ == "__main__":
    main()
```

At this point your callback functions will be executed every time Simple Slack Bot receives the appropriate event.


## Helper Functions & Callbacks Making Callbacks
Often times when writing a Slack Bot, you'll find yourself writing a few key functions that I found generic enough to include in Simple-Slack-Bot. The function names are pretty self explanatory but they are as follows:


* `write(channel, content)` - Writes a message to the channel as the bot
* `get_public_channel_ids()` - Gets all public channel ids
* `get_private_channel_ids()` - Gets all private channel ids
* `get_user_ids()` - Gets all user ids
* `get_users_in_channel(channel_id)` - Gets all users in a given channel
* `name_to_channel_id(name)` - Converts a channel name to its respected channel id
* `user_name_to_user_id(name)` - Converts a user name to its respected user id
* `channel_id_to_channel_name(channel_id)` - Converts a channel id to its respected channel name
* `user_id_to_user_name(user_id)` - Converts a user id to its respected user name

To gain access to these functions, simply design your class to accept an instance of SimpleSlackBot and call the functions on that reference.


## Event Firing A Callback Example - Hello World Bot

Assuming you followed the installation and integrating correctly, all you have to do is define a function. We'll do this by creating a `notify_hello` function.

```
def Foo():
  def notify_hello(self, dictionary):
    return "Hello World!"
```

After defining this function, all we have to do is inform Simple Slack Bot by creating an instance of of class `Foo`, which we'll call `foo` and register for hello events like so

 `register_hello(foo.notify)`

Any string your function returns will be written to the relevant Slack channel or direct message  by Simple Slack Bot.


## Executing

To run `app.py`, simply execute make

`$ make`
