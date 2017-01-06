# Simple Slack Bot

Simple Slack Bot attempts to factor out all the commonality between all Slack Bots, so that you can focus on writing your business logic.

See Slack's api here "https://api.slack.com/", as the dictionary that Simple Slack Bot provides is directly from Slack's API.


## Installing
To install, simply set the two environment variables

`SLACK_BOT_TOKEN` with your Slack Bot's API token

`BOT_ID` with the Slack ID of your bot


## Integrating

To integrate with Simple Slack Bot, simply create an instance of it and register for notifications using a callback function. This can be accomplished using the following code:


`app.py`
```
from simple_slack_bot import SimpleSlackBot


def main():
    simple_slack_bot = SimpleSlackBot()
    simple_slack_bot.register(replace_me_with_your_callback_function)
    simple_slack_bot.start()


if __name__ == "__main__":
    main()
```

At this point your `replace_me_with_your_callback_function` will be executed every time Simple Slack Bot receives a message.


### Call Back Example - Hello World Bot

Assuming you followed the installation and integrating correctly, all you have to do is define a function. We'll do this by creating a `notify` function.

```
def notify(self, dictionary):
    return "Hello World!"
```

and then pass the method `notify` to Simple Slack Bot by calling register (as demonstrated in Integration). Any string your function returns will be printed out by Simple Slack Bot.



## Executing

To run simply execute make

`$ make`
