import sys
sys.path.insert(0, "simple_slack_bot")
from simple_slack_bot import SimpleSlackBot
from example_component import ExampleComponent

def handler(request):
    print(f"got request {request._slack_event.json}")

    if(request._slack_event.event["type"] == "message"):
    	request.write("Herro, I received a message")

def main():
    simple_slack_bot = SimpleSlackBot(handler)

    simple_slack_bot.start()


if __name__ == "__main__":
    main()
