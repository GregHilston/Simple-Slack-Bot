import os
import sys
import time
import yaml
import logging.config
from slacker import Slacker
from .slack_request import SlackRequest
from slacksocket import SlackSocket
import simple_slack_bot.library.loggers.settings
from ..loggers import filters

class SimpleSlackBot:
    """
    Simplifies interacting with SlackClient. Allows users to register to
    specific events, get notified and run their business code
    """

    def __init__(self):
        """
        Initializes our Slack bot, setting up our logger and slack bot token
        """

        logging.config.dictConfig(yaml.safe_load(open("library/loggers/logging.yaml", 'rt')))
        self._logger = logging.getLogger(__name__)
        self._logger.setLevel(logging.DEBUG)

        self._SLACK_BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN")
        if self._SLACK_BOT_TOKEN is None:
            sys.exit("ERROR: environment variable SLACK_BOT_TOKEN is not set")

        self._slacker = Slacker(self._SLACK_BOT_TOKEN)
        self._slackSocket = SlackSocket(self._SLACK_BOT_TOKEN, translate=False)
        self._BOT_ID = self._slacker.auth.test().body["user_id"]
        self._registrations = {}  # our dictionary of event_types to a list of callbacks

        self._logger.info(f"set bot id to {self._BOT_ID}")
        self._logger.info("initialized")

    def register(self, event_type):
        """
        Registers a callback function to a a event type
        """

        def function_wrapper(callback):
            self._logger.info(f"registering callback {callback.__name__} to event type {event_type}")

            if event_type not in self._registrations:
                self._registrations[event_type] = []  # create an empty list
            self._registrations[event_type].append(callback)

        return function_wrapper

    def route_request_to_notify(self, request):
        """
        Routes the request to the correct notify
        """

        self._logger.debug(f"received an event of type {request.type}")
        self._logger.debug(f"slack event {request._slack_event.event}")

        if request.type in self._registrations:
            for callback in self._registrations[request.type]:
                callback(request)

    def listen(self):
        """
        Listens forever, updating on content
        """

        READ_WEBSOCKET_DELAY = 1  # 1 second delay between reading from firehose

        self._logger.info("began listening!")

        for slack_event in self._slackSocket.events():
            if slack_event:
                if slack_event.event and "bot_id" not in slack_event.event:  # We don't reply to bots
                    request = SlackRequest(self._slacker, slack_event)
                    self.route_request_to_notify(request)

            time.sleep(READ_WEBSOCKET_DELAY)

        self._logger.info("Keyboard interrupt received. Gracefully shutting down")
        sys.exit(0)

    def start(self):
        """
        Connect the slack bot to the chatroom and begin listening to channel
        """

        ok = self._slacker.rtm.start().body["ok"]

        if ok:
            self._logger.info("started!")
            self.listen()
        else:
            self._logger.error("Connection failed. Are you connected to the internet? Potentially invalid Slack token? "
                               "Check environment variable and \"SLACK_BOT_TOKEN\"")
