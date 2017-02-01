import os, sys, time, logging
from slackclient import SlackClient


class SlackRequest(object):

    def __init__(self, client, data=None):
        """
        :param client: SlackClient class
        :type client: SlackClient
        :param data: data returned by the server after an API call
        :type data: dict, if not provided some functions may not work properly
        """
        self.data = data
        self.client = client

    @property
    def type(self):
        return self.data["type"]

    @property
    def channel(self):
        return self.data.get("channel")

    @property
    def message(self):
        return self.data.get("text")

    def write(self, content, channel=None, **kwargs):
        """
        Writes the content to the channel

        :param content: The text you wish to send
        :param channel: By default send to same channel request came from
        :param kwargs: any extra arguments you want to pass to chat.postMessage slack API
        """
        if channel is None and self.data:
            channel = self.channel
        defaults = {"as_user": True}
        defaults.update(kwargs)
        self.client.api_call("chat.postMessage", channel=channel, text=content, **defaults)
        # self._logger.debug("wrote {}".format(content))

    def upload(self, output_filename, content, channel=None, **kwargs):
        """
        Upload the content or input_filename's content to the channel
        @param output_filename: filename that should appear to the enduser
        @param content: content to be uploaded can be string or an opened file
        @param kwargs: any extra parameters you wish to pass to the upload api
        """
        params = {
            "channels": channel or self.channel, "filename": output_filename}
        if hasattr(content, "read"):
            params["file"] = content
        else:
            params["content"] = content
        params.update(kwargs)
        response = self.client.api_call("files.upload", **params)
        # self._logger.debug("uploaded {} with response {}".format(content, response))


class SimpleSlackBot():
    """
    Simplifies interacting with SlackClient. Allows users to register to
    specific events, get notified, run business code and return a reply for
    writing back to Slack
    """

    def __init__(self):
        self._logger = self.initialize_logger()

        self._BOT_ID = os.environ.get("BOT_ID")
        if self._BOT_ID is None:
            sys.exit("ERROR: environment variable BOT_ID is not set")

        self._SLACK_BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN")
        if self._SLACK_BOT_TOKEN is None:
            sys.exit("ERROR: environment variable SLACK_BOT_TOKEN is not set")

        self._slack_client = SlackClient(self._SLACK_BOT_TOKEN)
        self._hello_callbacks = []
        self._mentions_callbacks = []
        self._public_channels_callbacks = []
        self._private_channels_callbacks = []
        self._direct_messages_callbacks = []
        self._user_names = []
        self._user_id_mentions = []
        self._user_name_mentions = []
        self._logger.info("initialized")
        self.cache_user_names_and_ids()

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
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
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
        self._user_id_mentions.append(AT_USER_PREFIX + str(self.user_name_to_user_id(str(self._BOT_ID))) + AT_USER_SUFFIX)
        self._user_name_mentions.append(AT_USER_PREFIX + str(self._BOT_ID) + AT_USER_SUFFIX)

        for user_id, user_name in zip(self._user_ids, self._user_names):
            self._user_id_mentions.append(AT_USER_PREFIX + user_id + AT_USER_SUFFIX)
            self._user_name_mentions.append(AT_USER_PREFIX + user_name + AT_USER_SUFFIX)


    def get_slack_client(self):
        """
        Returns SimpleSlackBot's SlackClient.

        This is useful if you are writing more advanced bot and want complete
        access to all SlackClient has to offer.
        """

        return self._slack_client


    def start(self):
        """
        Connect the slack bot to the chatroom and begin listening to channel
        """

        ret = self._slack_client.rtm_connect()

        if ret:
            self._logger.info("started!")
            self.listen()
        else:
            self._logger.error("Connection failed. Are you connected to the internet?"
                         " Potentially invalid Slack token or bot ID? Check"
                         " environment variables \"BOT_ID\" and \"SLACK_BOT_TOKEN\"")


    def route_request_to_notify(self, request):
        """
        Routes the request to the correct notify
        """

        event_type = request.type
        self._logger.debug("received an event of type {}".format(event_type))
        self._logger.debug("data {}".format(request.data))

        if event_type == "hello":
            self.notify_hello(request)

        elif event_type == "message":

            self._logger.debug("printing request.message {}".format(self._user_name_mentions, request.message))

            if any(user_id_mention in request.message for user_id_mention in self._user_id_mentions):
                self.notify_mentions(request)

            elif request.channel in self.get_public_channel_ids():
                self.notify_public_channels_messages(request)

            elif request.channel in self.get_private_channel_ids():
                self.notify_private_channels_messages(request)

            elif request.data["user"] in self.get_user_ids():
                self.notify_direct_messages(request)

            else:
                self._logger.error("Unsure how to route {}".format(request.data))


    def listen(self):
        """
        Listens forever, updating on content
        """

        READ_WEBSOCKET_DELAY = 1 # 1 second delay between reading from firehose

        self._logger.info("began listening!")

        while True:
            try:
                json_list = self._slack_client.rtm_read()

                if json_list and len(json_list) > 0:
                    for dictionary in json_list:
                        if dictionary and "bot_id" not in dictionary: # We don't reply to bots
                            request = SlackRequest(self.get_slack_client(), dictionary)
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
            self._logger.info("registered {} to hello event".format(str(callback)))
        else:
            self._logger.warning("did not register {} to hello event, as already registered".format(str(callback)))


    def notify_hello(self, request):
        """
        Notifies observers of hello events. Often used for bot initialization
        """

        for callback in self._hello_callbacks:
            callback(request)
            self._logger.debug("notified {} of hello event".format(callback))


    def register_mentions(self, callback):
        """
        Registers callback to mentions of this bot, by BOT_ID
        """

        if callback not in self._mentions_callbacks:
            self._mentions_callbacks.append(callback)
            self._logger.info("registered {} to mentions".format(str(callback)))
        else:
            self._logger.warning("did not register {} to mentions, as already registered".format(str(callback)))


    def notify_mentions(self, request):
        """
        Notifies observers of the mentions event of this bot, by BOT_ID
        """

        for callback in self._mentions_callbacks:
            callback(request)
            self._logger.debug("notified {} of mentions event".format(callback))


    def register_public_channels_messages(self, callback):
        """
        Registers callback to all public channels messages
        """

        if callback not in self._public_channels_callbacks:
            self._public_channels_callbacks.append(callback)
            self._logger.info("registered {} to public channels".format(str(callback)))
        else:
            self._logger.warning("did not register {} to public channels, as already registered".format(str(callback)))


    def notify_public_channels_messages(self, request):
        """
        Notifies observers of the all public channel message events
        """

        for callback in self._public_channels_callbacks:
            callback(request)
            self._logger.debug("notified {} of all public channels event".format(callback))


    def register_private_channels_messages(self, callback):
        """
        Registers callback to all private channel message events
        """

        if callback not in self._private_channels_callbacks:
            self._private_channels_callbacks.append(callback)
            self._logger.info("registered {} to private channels".format(str(callback)))
        else:
            self._logger.warning("did not register {} to private channels event, as already registered".format(str(callback)))


    def notify_private_channels_messages(self, request):
        """
        Notifies observers of the all private channel message events
        """

        for callback in self._private_channels_callbacks:
            callback(request)
            self._logger.debug("notified {} of all private channels event".format(callback))


    def register_direct_messages(self, callback):
        """
        Registers callback to all direct messages
        """

        if callback not in self._direct_messages_callbacks:
            self._direct_messages_callbacks.append(callback)
            self._logger.info("registered {} to direct messages event".format(str(callback)))
        else:
            self._logger.warning("did not register {} to direct messages event, as already registered".format(str(callback)))


    def notify_direct_messages(self, request):
        """
        Notifies observers of the all direct messages event
        """

        for callback in self._direct_messages_callbacks:
            callback(request)
            self._logger.debug("notified {} of all direct messages event".format(callback))


    def get_public_channel_ids(self):
        """
        Gets all public channel ids
        """

        public_channel_ids = []

        public_channels = self._slack_client.api_call("channels.list", token=self._SLACK_BOT_TOKEN)
        for channel in public_channels["channels"]:
            public_channel_ids.append(channel["id"])

        if len(public_channel_ids) == 0:
            self._logger.warning("got no public channel ids")
        else:
            self._logger.debug("got public channel ids {}".format(public_channel_ids))

        return public_channel_ids


    def get_private_channel_ids(self):
        """
        Gets all private channel ids
        """

        private_channel_ids = []

        private_channels = self._slack_client.api_call("groups.list", token=self._SLACK_BOT_TOKEN)

        self._logger.info("private_channels {}".format(private_channels))
        for private_channel in private_channels["groups"]:
            private_channels.append(channel["id"])

        if len(private_channel_ids) == 0:
            self._logger.warning("got no private channel ids")
        else:
            self._logger.debug("got private channel ids {}".format(private_channel_ids))

        return private_channel_ids


    def get_user_ids(self):
        """
        Gets all user ids
        """

        user_ids = []

        users_list = self._slack_client.api_call("users.list", token=self._SLACK_BOT_TOKEN)
        for user in users_list["members"]:
            user_ids.append(user["id"])

        if len(user_ids) == 0:
            self._logger.warning("got no user ids")
        else:
            self._logger.debug("got user ids {}".format(user_ids))

        return user_ids


    def get_user_names(self):
        """
        Gets all user names
        """

        user_names = []

        users_list = self._slack_client.api_call("users.list", token=self._SLACK_BOT_TOKEN)
        for user in users_list["members"]:
            user_names.append(user["name"])

        if len(user_names) == 0:
            self._logger.warning("got no user names")
        else:
            self._logger.debug("got user names {}".format(user_names))

        return user_names


    def get_users_in_channel(self, channel_id):
        """
        Gets all users in a given channel
        """

        user_ids = []

        channels_list = self._slack_client.api_call("channels.list", token=self._SLACK_BOT_TOKEN)
        for channel in channels_list["channels"]:
              if channel["id"] == channel_id:
                for user_id in channel["members"]:
                    user_ids.append(user_id)

        if len(user_ids) == 0:
            self._logger.warning("got no user ids for channel {}".format(channel_id))
        else:
            self._logger.debug("got user ids {}".format(user_ids))

        return user_ids


    def channel_name_to_channel_id(self, name):
        """
        Converts a channel name to its respected channel id
        """

        channels_list = self._slack_client.api_call("channels.list", token=self._SLACK_BOT_TOKEN)

        for channel in channels_list["channels"]:
            if channel["name"] == name:
                self._logger.debug("converted {} to {}".format(channel["name"], channel["id"]))
                return channel["id"]

        self._logger.warning("could not convert channel name {} to an id".format(name))


    def user_name_to_user_id(self, name):
        """
        Converts a user name to its respected user id
        """

        users_list = self._slack_client.api_call("users.list", token=self._SLACK_BOT_TOKEN)

        for user in users_list["members"]:
            if user["name"] == name:
                self._logger.debug("converted {} to {}".format(name, user["id"]))
                return user["id"]

        self._logger.warning("could not convert user name {} to a user id".format(name))


    def channel_id_to_channel_name(self, channel_id):
        """
        Converts a channel id to its respected channel name
        """

        channels_list = self._slack_client.api_call("channels.list", token=self._SLACK_BOT_TOKEN)

        for channel in channels_list["channels"]:
            if channel["id"] == channel_id:
                self._logger.debug("converted {} to {}".format(channel_id, channel["name"]))
                return channel["name"]

        self._logger.warning("could not convert channel id {} to a name".format(channel_id))


    def user_id_to_user_name(self, user_id):
        """
        Converts a user id to its respected user name
        """

        users_list = self._slack_client.api_call("users.list", token=self._SLACK_BOT_TOKEN)

        for user in users_list["members"]:
            if user["id"] == user_id:
                self._logger.debug("converted {} to {}".format(user_id, user["name"]))
                return user["name"]

        self._logger.warning("could not convert user id {} to a name".format(user_id))
