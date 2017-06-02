import os, sys, time, logging
from slacker import Slacker
from slack_request import SlackRequest
from slacksocket import SlackSocket


class SimpleSlackBot():
    """
    Simplifies interacting with SlackClient. Allows users to register to
    specific events, get notified and run their business code
    """

    def __init__(self):
        """
        Initiazes our Slack bot, setting up our logger and slack bot token
        """
        
        self._logger = self.initialize_logger()

        self._SLACK_BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN")
        if self._SLACK_BOT_TOKEN is None:
            sys.exit("ERROR: environment variable SLACK_BOT_TOKEN is not set")

        self._slacker = Slacker(self._SLACK_BOT_TOKEN)
        self._slackSocket = SlackSocket(self._SLACK_BOT_TOKEN, translate=False)
        self._BOT_ID = self._slacker.auth.test().body["user_id"]
        self._registrations = {} # our dictionary of event_types to a list of callbacks

        self._logger.info(f"set bot id to {self._BOT_ID}")
        self._logger.info("initialized")


    def initialize_logger(self):
        """
        Initializes and returns a logger
        """

        # setting up our logger to write to a log file
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.DEBUG) # Process all levels of logging messages

        # create file handler
        file_handler = logging.FileHandler(__name__  + ".log", mode='w')
        file_handler.setLevel(logging.DEBUG)

        # create stream handler
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging.DEBUG)

        # create formatter and add it to the handlers
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        file_handler.setFormatter(formatter)
        stream_handler.setFormatter(formatter)

        # add the handlers to the logger
        logger.addHandler(file_handler)
        logger.addHandler(stream_handler)

        return logger


    def register(self, event_type):
        """
        Registers a callback function to a a event type
        """
        
        def function_wrapper(callback):
            self._logger.info(f"registering callback {callback.__name__} to event type {event_type}")

            if event_type not in self._registrations:
                self._registrations[event_type] = [] # create an empty list
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

        READ_WEBSOCKET_DELAY = 1 # 1 second delay between reading from firehose

        self._logger.info("began listening!")

        while True:
            try:
                for slack_event in self._slackSocket.events():
                    if slack_event:
                        if slack_event.event and "bot_id" not in slack_event.event: # We don't reply to bots
                            request = SlackRequest(self._slacker, slack_event)
                            self.route_request_to_notify(request)

                    time.sleep(READ_WEBSOCKET_DELAY)
            except KeyboardInterrupt:
                self._logger.info("User ended listening. Gracefully shutting down")
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
            self._logger.error("Connection failed. Are you connected to the "
                        "internet? Potentially invalid Slack token? Check "
                        " environment variable and \"SLACK_BOT_TOKEN\"")