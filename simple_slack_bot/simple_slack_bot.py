import os, sys, time, logging
from slacker import Slacker
from slack_request import SlackRequest
from slacksocket import SlackSocket


class SimpleSlackBot():
    """
    Simplifies interacting with SlackClient. Allows users to register to
    specific events, get notified, run business code and return a reply for
    writing back to Slack
    """

    def __init__(self):
        self._logger = self.initialize_logger()

        self._SLACK_BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN")
        if self._SLACK_BOT_TOKEN is None:
            sys.exit("ERROR: environment variable SLACK_BOT_TOKEN is not set")

        self._slacker = Slacker(self._SLACK_BOT_TOKEN)
        # translate will lookup and replace user and channel IDs with their human-readable names. default true. 
        self._slackSocket = SlackSocket(self._SLACK_BOT_TOKEN, translate=False)
        self._BOT_ID = self._slacker.auth.test().body["user_id"]
        self._hello_callbacks = []
        self._mentions_callbacks = []
        self._public_channels_callbacks = []
        self._private_channels_callbacks = []
        self._direct_messages_callbacks = []
        self._user_names = []
        self._user_id_mentions = []
        self._user_name_mentions = []
        self.cache_user_names_and_ids()

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
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - "
                                      "%(message)s")
        file_handler.setFormatter(formatter)
        stream_handler.setFormatter(formatter)

        # add the handlers to the logger
        logger.addHandler(file_handler)
        logger.addHandler(stream_handler)

        return logger


    def cache_user_names_and_ids(self):
        """
        Caches user names and ids
        """

        self._user_ids = self.get_user_ids()
        self._user_names = self.get_user_names()
        self.cache_mention_strings()


    def cache_mention_strings(self):
        """
        Caches the mention strings based on the user name and id cache
        """

        AT_USER_PREFIX = "<@"
        AT_USER_SUFFIX = ">"
        self._user_id_mentions = []
        self._user_name_mentions = []

        # add this bot
        self._user_id_mentions.append(AT_USER_PREFIX + (
            str(self.user_name_to_user_id(str(self._BOT_ID))) +
            AT_USER_SUFFIX))
        self._user_name_mentions.append(AT_USER_PREFIX + str(self._BOT_ID) + (
            AT_USER_SUFFIX))

        for user_id, user_name in zip(self._user_ids, self._user_names):
            self._user_id_mentions.append(AT_USER_PREFIX + user_id + (
                AT_USER_SUFFIX))
            self._user_name_mentions.append(AT_USER_PREFIX + user_name + (
                AT_USER_SUFFIX))


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


    def route_request_to_notify(self, request):
        """
        Routes the request to the correct notify
        """

        self._logger.debug(f"received an event of type {request.type}")
        self._logger.debug(f"slack event {request._slack_event.event}")

        if request.type == "hello":
            self.notify_hello(request)

        elif request.type == "message":
            self._logger.debug(f"printing request.message {request.message}")

            if any(user_id_mention in request.message for user_id_mention in
                self._user_id_mentions):
                self.notify_mentions(request)

            elif request.channel in self.get_public_channel_ids():
                self.notify_public_channels_messages(request)

            elif request.channel in self.get_private_channel_ids():
                self.notify_private_channels_messages(request)

            elif request._slack_event.event["user"] in self.get_user_ids():
                self.notify_direct_messages(request)

            else:
                self._logger.error(f"Unsure how to route {request._slack_event.json}")
        else:
            self._logger.error(f"Unsure how to route {request._slack_event.json}")


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


    def register_hello(self, callback):
        """
        Registers callback to hello event
        """

        if callback not in self._hello_callbacks:
            self._hello_callbacks.append(callback)
            self._logger.info(f"registered {str(callback)} to hello event")
        else:
            self._logger.warning(f"did not register {str(callback)} to hello event, as already registered")


    def notify_hello(self, request):
        """
        Notifies observers of hello events. Often used for bot initialization
        """

        for callback in self._hello_callbacks:
            callback(request)
            self._logger.debug(f"notified {str(callback)} of hello event")


    def register_mentions(self, callback):
        """
        Registers callback to mentions of this bot, by BOT_ID
        """

        if callback not in self._mentions_callbacks:
            self._mentions_callbacks.append(callback)
            self._logger.info("registered {str(callback)} to mentions")
        else:
            self._logger.warning(f"did not register {str(callback)} to mentions, as already registered")


    def notify_mentions(self, request):
        """
        Notifies observers of the mentions event of this bot, by BOT_ID
        """

        for callback in self._mentions_callbacks:
            callback(request)
            self._logger.debug(f"notified {str(callback)} of mentions event")


    def register_public_channels_messages(self, callback):
        """
        Registers callback to all public channels messages
        """

        if callback not in self._public_channels_callbacks:
            self._public_channels_callbacks.append(callback)
            self._logger.info(f"registered {str(callback)} to public channels")
        else:
            self._logger.warning(f"did not register {str(callback)} to public channels, as already registered")


    def notify_public_channels_messages(self, request):
        """
        Notifies observers of the all public channel message events
        """

        for callback in self._public_channels_callbacks:
            callback(request)
            self._logger.debug(f"notified {str(callback)} of all public channels event")


    def register_private_channels_messages(self, callback):
        """
        Registers callback to all private channel message events
        """

        if callback not in self._private_channels_callbacks:
            self._private_channels_callbacks.append(callback)
            self._logger.info(f"registered {str(callback)} to private channels")
        else:
            self._logger.warning(f"did not register {str(callback)} to private channels event, as already registered")


    def notify_private_channels_messages(self, request):
        """
        Notifies observers of the all private channel message events
        """

        for callback in self._private_channels_callbacks:
            callback(request)
            self._logger.debug(f"notified {str(callback)} of all private channels event")


    def register_direct_messages(self, callback):
        """
        Registers callback to all direct messages
        """

        if callback not in self._direct_messages_callbacks:
            self._direct_messages_callbacks.append(callback)
            self._logger.info(f"registered {str(callback)} to direct messages event")
        else:
            self._logger.warning(f"did not register {str(callback)} to direct messages event, as already registered")


    def notify_direct_messages(self, request):
        """
        Notifies observers of the all direct messages event
        """

        for callback in self._direct_messages_callbacks:
            callback(request)
            self._logger.debug(f"notified {str(callback)} of all direct messages event")


    def get_public_channel_ids(self):
        """
        Gets all public channel ids
        """

        public_channel_ids = []

        public_channels = self._slacker.channels.list().body["channels"]
        for channel in public_channels:
            public_channel_ids.append(channel["id"])

        if len(public_channel_ids) == 0:
            self._logger.warning("got no public channel ids")
        else:
            self._logger.debug(f"got public channel ids {public_channel_ids}")

        return public_channel_ids


    def get_private_channel_ids(self):
        """
        Gets all private channel ids
        """

        private_channel_ids = []

        private_channels = self._slacker.groups.list().body["groups"]

        self._logger.info(f"private_channels {private_channels}")
        for private_channel in private_channels:
            private_channels.append(channel["id"])

        if len(private_channel_ids) == 0:
            self._logger.warning("got no private channel ids")
        else:
            self._logger.debug(f"got private channel ids {private_channel_ids}")

        return private_channel_ids


    def get_user_ids(self):
        """
        Gets all user ids
        """

        user_ids = []

        users = self._slacker.users.list().body["members"]
        for user in users:
            user_ids.append(user["id"])

        if len(user_ids) == 0:
            self._logger.warning("got no user ids")
        else:
            self._logger.debug(f"got user ids {user_ids}")

        return user_ids


    def get_user_names(self):
        """
        Gets all user names
        """

        user_names = []

        users = self._slacker.users.list().body["members"]
        for user in users:
            user_names.append(user["name"])

        if len(user_names) == 0:
            self._logger.warning("got no user names")
        else:
            self._logger.debug(f"got user names {user_names}")

        return user_names


    def get_users_in_channel(self, channel_id):
        """
        Gets all users in a given channel
        """

        user_ids = []

        channels_list = self._slacker.channels.list().body["channels"]
        for channel in channels_list["channels"]:
              if channel["id"] == channel_id:
                for user_id in channel["members"]:
                    user_ids.append(user_id)

        if len(user_ids) == 0:
            self._logger.warning(f"got no user ids for channel {channel_id}")
        else:
            self._logger.debug(f"got user ids {user_ids}")

        return user_ids


    def channel_name_to_channel_id(self, name):
        """
        Converts a channel name to its respected channel id
        """

        channels_list = self._slacker.channels.list().body["channels"]

        for channel in channels_list["channels"]:
            if channel["name"] == name:
                self._logger.debug(f"converted {channel['name']} to {channel['id']}")
                return channel["id"]

        self._logger.warning(f"could not convert channel name {name} to an id")


    def user_name_to_user_id(self, name):
        """
        Converts a user name to its respected user id
        """

        users = self._slacker.users.list().body["members"]

        for user in users:
            if user["name"] == name:
                self._logger.debug(f"converted {name} to {user['id']}")
                return user["id"]

        self._logger.warning(f"could not convert user name {name} to a user id")


    def channel_id_to_channel_name(self, channel_id):
        """
        Converts a channel id to its respected channel name
        """

        channels_list = self._slacker.channels.list().body["channels"]

        for channel in channels_list["channels"]:
            if channel["id"] == channel_id:
                self._logger.debug("converted {} to {}".format(channel_id, channel["name"]))
                return channel["name"]

        self._logger.warning(f"could not convert channel id {channel_id} to a name")


    def user_id_to_user_name(self, user_id):
        """
        Converts a user id to its respected user name
        """

        users_list = self._slack_client.api_call("users.list", token=self._SLACK_BOT_TOKEN)

        for user in users_list["members"]:
            if user["id"] == user_id:
                self._logger.debug(f"converted {user_id} to {user['name']}")
                return user["name"]

        self._logger.warning(f"could not convert user id {user_id} to a name")
