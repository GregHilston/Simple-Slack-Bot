import os, sys, time, logging
from slackclient import SlackClient
from registerable import Registerable

# setting up our logger to write to a log file
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG) # Process all levels of logging messages

# create file handler
file_handler = logging.FileHandler(__name__  + ".log", mode='w')
file_handler.setLevel(logging.DEBUG)

# create stream handler
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.INFO)

# create formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
stream_handler.setFormatter(formatter)

# add the handlers to the logger
logger.addHandler(file_handler)
logger.addHandler(stream_handler)


class SimpleSlackBot(Registerable):
    """
    Simplifies interacting with SlackClient. Allows users to register to
    specific events, get notified, run business code and return a reply for
    writing back to Slack
    """

    def __init__(self):
        self._BOT_ID = os.environ.get("BOT_ID")
        self._SLACK_TOKEN = os.environ.get("SLACK_BOT_TOKEN")
        self._slack_client = SlackClient(self._SLACK_TOKEN)
        self._hello_callbacks = []
        self._channels_callbacks = []

        logger.info("initialized")


    def start(self):
        """
        Connect the slack bot to the chatroom and begin listening to channel
        """

        ret = self._slack_client.rtm_connect()

        if ret:
            logger.info("started!")
            self.listen()
        else:
            logger.error("Connection failed. Are you connected to the internet?"
                         " Potentially invalid Slack token or bot ID? Check"
                         " environment variables.")


    def listen(self):
        """
        Listens forever, updating on content
        """

        READ_WEBSOCKET_DELAY = 1 # 1 second delay between reading from firehose
        running = True

        logger.info("began listening!")

        while True:
            try:
                json_list = self._slack_client.rtm_read()


                if json_list and len(json_list) > 0:
                    for dictionary in json_list:
                        if dictionary and "bot_id" not in dictionary: # We don't reply to bots
                            event_type = dictionary["type"]
                            logger.debug("received an event of type {}".format(event_type))

                            if event_type == "hello":
                                self.notify_hello(dictionary)

                            elif event_type == "message":
                                self.notify_channels(dictionary)

                time.sleep(READ_WEBSOCKET_DELAY)
            except KeyboardInterrupt:
                logger.info("User ended listening. Gracefully shutting down")
                sys.exit(0)


    def register_hello(self, callback):
        """
        Registers callback to hello event
        """

        if callback not in self._hello_callbacks:
            self._hello_callbacks.append(callback)
            logger.info("registered {} to hello event".format(str(callback)))
        else:
            logger.warning("did not register {} to hello event, as already registerd".format(str(callback)))


    def notify_hello(self, dictionary):
        """
        Notifies observers of the hello event. Often used for bot initialization
        """

        for callback in self._hello_callbacks:
            reply = callback(dictionary)
            logger.debug("notified {} of hello event".format(callback))


    def register_channels(self, callback):
        """
        Registers callback to all channels
        """

        if callback not in self._channels_callbacks:
            self._channels_callbacks.append(callback)
            logger.info("registered {} to channels".format(str(callback)))
        else:
            logger.warning("did not register {} to channels, as already registerd".format(str(callback)))


    def notify_channels(self, dictionary):
        """
        Notifies observers of the channels event
        """

        for callback in self._channels_callbacks:
            reply = callback(dictionary)
            logger.debug("notified {} of channels event".format(callback))

            if reply:
                self.write(dictionary["channel"], reply)


    def write(self, channel, content):
        """
        Writes the content to the channel
        """

        self._slack_client.api_call("chat.postMessage", channel=channel, text=content, as_user=True)
        logger.debug("wrote {}".format(content))
