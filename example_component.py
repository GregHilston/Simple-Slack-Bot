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
