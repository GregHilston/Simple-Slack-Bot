from simple_slack_bot import SimpleSlackBot

simple_slack_bot = SimpleSlackBot()


@simple_slack_bot.register("hello")
def hello_callback(request):
    simple_slack_bot._logger.info(f"ExampleComponent.hello_callback got request {request}")
    request.write("Hello!")


@simple_slack_bot.register("message")
def pong_callback(request):
    simple_slack_bot._logger.info(f"ExampleComponent.pong_callback got request {request}")

    if request.message.lower() == "ping":
        request.write("Pong")


def main():
    simple_slack_bot.start()


if __name__ == "__main__":
    main()
