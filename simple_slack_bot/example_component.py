from simple_slack_bot import SimpleSlackBot


simple_slack_bot = SimpleSlackBot()


@simple_slack_bot.register("hello")
def hello_callback(request):
	simple_slack_bot._logger.info(f"ExampleComponent.hello_callback got request {request}")


def main():
	simple_slack_bot.start()
	example_component.start()
	

if __name__ == "__main__":
    main()