from simple_slack_bot.simple_slack_bot import SimpleSlackBot

simple_slack_bot = SimpleSlackBot(debug=True)


@simple_slack_bot.register("hello")
def hello_callback(request):
    request.write("Hello!")


@simple_slack_bot.register("user_typing")
def user_typing_callback(request):
    user_id = simple_slack_bot.helper_user_id_to_user_name(request._slack_event.event['user'])
    request.write(f"I see you typing {user_id}")


@simple_slack_bot.register("message")
def pong_callback(request):
    if request.message.lower() == "ping":
        request.write("Pong")


def main():
    simple_slack_bot.start()


if __name__ == "__main__":
    main()
