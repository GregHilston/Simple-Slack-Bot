from simple_slack_bot import SimpleSlackBot
from hello_world_component import HelloWorldComponent

def main():
    simple_slack_bot = SimpleSlackBot()

    hello_world_component = HelloWorldComponent()
    simple_slack_bot.register_hello(hello_world_component.hello)
    simple_slack_bot.register_mentions(hello_world_component.mentions)
    simple_slack_bot.register_public_channels_message(hello_world_component.public_channels)
    simple_slack_bot.register_direct_messages(hello_world_component.direct_messages)

    simple_slack_bot.start()


if __name__ == "__main__":
    main()
