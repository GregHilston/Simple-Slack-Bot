import sys
sys.path.insert(0, "simple_slack_bot")
from simple_slack_bot import SimpleSlackBot


def main():
    simple_slack_bot = SimpleSlackBot()
    simple_slack_bot.start()


if __name__ == "__main__":
    main()
