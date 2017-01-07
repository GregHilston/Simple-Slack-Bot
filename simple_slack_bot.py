import os, sys, time, logging
from slackclient import SlackClient

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


class SimpleSlackBot():
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
        self._mentions_callbacks = []
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
        AT_BOT = "<@" + self._BOT_ID + ">" # Used for mentions
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
                            logger.debug("dictionary {}".format(dictionary))

                            if event_type == "hello":
                                self.notify_hello(dictionary)

                            elif event_type == "message" and AT_BOT in dictionary["text"]:
                                self.notify_mentions(dictionary)

                            elif event_type == "message" and AT_BOT not in dictionary["text"]:
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
            logger.warning("did not register {} to hello event, as already registered".format(str(callback)))


    def notify_hello(self, dictionary):
        """
        Notifies observers of hello events. Often used for bot initialization
        """

        for callback in self._hello_callbacks:
            callback(dictionary)
            logger.debug("notified {} of hello event".format(callback))


    def register_mentions(self, callback):
        """
        Registers callback to mentions of this bot, by BOT_ID
        """

        if callback not in self._mentions_callbacks:
            self._mentions_callbacks.append(callback)
            logger.info("registered {} to mentions".format(str(callback)))
        else:
            logger.warning("did not register {} to mentions, as already registered".format(str(callback)))


    def notify_mentions(self, dictionary):
        """
        Notifies observers of the mentions event of this bot, by BOT_ID
        """

        for callback in self._mentions_callbacks:
            reply = callback(dictionary)
            logger.debug("notified {} of mentions event".format(callback))

            if reply:
                self.write(dictionary["channel"], reply)


    def register_channels(self, callback):
        """
        Registers callback to all channels
        """

        if callback not in self._channels_callbacks:
            self._channels_callbacks.append(callback)
            logger.info("registered {} to channels".format(str(callback)))
        else:
            logger.warning("did not register {} to channels, as already registered".format(str(callback)))


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


    def get_channel_ids(self):
        """
        Gets all channel ids
        """

        channel_ids = []

        channels_list = self._slack_client.api_call("channels.list", token=self._SLACK_TOKEN)
        for channel in channels_list["channels"]:
            channel_ids.append(channel["id"])

        if len(channel_ids) == 0:
            logger.warning("got no channel ids")
        else:
            logger.debug("got channel ids {}".format(channel_ids))

        return channel_ids


    def get_user_ids(self):
        """
        Gets all user ids
        """

        user_ids = []

        users_list = self._slack_client.api_call("users.list", token=self._SLACK_TOKEN)
        for user in users_list["members"]:
            user_ids.append(user["id"])

        if len(user_ids) == 0:
            logger.warning("got no user ids")
        else:
            logger.debug("got user ids {}".format(user_ids))

        return user_ids

    def get_users_in_channel(self, channel_id):
        """
        Gets all users in a given channel
        """

        user_ids = []

        channels_list = self._slack_client.api_call("channels.list", token=self._SLACK_TOKEN)
        for channel in channels_list["channels"]:
            if channel["id"] == channel_id:
                for user_id in channel["members"]:
                    user_ids.append(user_id)

        if len(user_ids) == 0:
            logger.warning("got no user ids for channel {}".format(channel_id))
        else:
            logger.debug("got user ids {}".format(user_ids))

        return user_ids


    def name_to_channel_id(self, name):
        """
        Converts a name to its respected channel id
        """

        channels_list = self._slack_client.api_call("channels.list", token=self._SLACK_TOKEN)

        for channel in channels_list["channels"]:
            if channel["name"] == name:
                logger.debug("converted {} to {}".format(channel["name"], channel["id"]))
                return channel["id"]

        logger.warning("could not convert channel name {} to an id".format(name))


    def name_to_user_id(self, name):
        """
        Converts a name to its respected user id
        """

        users_list = self._slack_client.api_call("users.list", token=self._SLACK_TOKEN)

        for user in users_list["members"]:
            if user["name"] == name:
                logger.debug("converted {} to {}".format(name, user["id"]))
                return user["id"]

        logger.warning("could not convert name {} to a user id".format(name))


    def channel_id_to_name(self, channel_id):
        """
        Converts a channel id to its respected name
        """

        channels_list = self._slack_client.api_call("channels.list", token=self._SLACK_TOKEN)

        for channel in channels_list["channels"]:
            if channel["id"] == channel_id:
                logger.debug("converted {} to {}".format(channel_id, channel["name"]))
                return channel["name"]

        logger.warning("could not convert channel id {} to a name".format(channel_id))


    def user_id_to_name(self, user_id):
        """
        Converts a user id to its respected name
        """

        users_list = self._slack_client.api_call("users.list", token=self._SLACK_TOKEN)

        for user in users_list["members"]:
            if user["id"] == user_id:
                logger.debug("converted {} to {}".format(user_id, user["name"]))
                return user["name"]

        logger.warning("could not convert user id {} to a name".format(user_id))
