import os, sys, time, logging
from slackclient import SlackClient


# setting up our logger to write to a log file
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG) # Process all levels of logging messages

# create file handler
file_handler = logging.FileHandler(__name__  + ".log")
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


class SimpleSlackBot:
    def __init__(self):
        self._BOT_ID = os.environ.get("BOT_ID")
        self._SLACK_TOKEN = os.environ.get("SLACK_BOT_TOKEN")
        self._slack_client = SlackClient(self._SLACK_TOKEN)
        self._observer_callbacks = []

        logger.info("initialized")

        logger.info("getting channel list")
        logger.info(self._slack_client.api_call("users.list"))

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
                    logger.debug("received an event!")
                    for dictionary in json_list:
                        logger.debug(dictionary)
                        # print("type {}".format(str(dictionary["type"])))
                        if dictionary and str(dictionary["type"]) == "message":
                            if "bot_id" in dictionary:
                                continue
                            self.update(dictionary)

                time.sleep(READ_WEBSOCKET_DELAY)
            except KeyboardInterrupt:
                logger.info("User ended listening. Gracefully shutting down")
                sys.exit(0)


    def register(self, callback):
        """
        Registers the observer to receive updates from the observable
        """

        if callback not in self._observer_callbacks:
            self._observer_callbacks.append(callback)
            logger.info("registered {}".format(str(callback)))
        else:
            logger.warning("did not register {}, as already registerd".format(str(callback)))

    def update(self, dictionary):
        """
        Notifies observers of the dictionary
        """

        for callback in self._observer_callbacks:
            reply = callback(dictionary)
            logger.debug("notified {}".format(callback))

            if reply:
                self.write(dictionary, reply)


    def write(self, dictionary, content):
        """
        Writes the content to the channel
        """

        self._slack_client.api_call("chat.postMessage", channel=dictionary["channel"], text=content, as_user=True)
        logger.debug("wrote {}".format(content))
