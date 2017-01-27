import sys
sys.path.insert(0, "simple_slack_bot")
from simple_slack_bot import SimpleSlackBot
from example_component import ExampleComponent


def main():
    simple_slack_bot = SimpleSlackBot()

    example_component = ExampleComponent()
    simple_slack_bot.register_hello(example_component.hello)
    simple_slack_bot.register_mentions(example_component.mentions)
    simple_slack_bot.register_public_channels_messages(example_component.public_channels_messages)
    simple_slack_bot.register_private_channels_messages(example_component.private_channels_messages)
    simple_slack_bot.register_direct_messages(example_component.direct_messages)

    simple_slack_bot.start()


if __name__ == "__main__":
    main()
