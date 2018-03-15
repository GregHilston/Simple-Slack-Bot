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

        self._logger.debug(f"set bot id to {self._BOT_ID}")
        self._logger.debug("initialized")

    def register(self, event_type):
        """
        Registers a callback function to a a event type
        """

        def function_wrapper(callback):
            self._logger.debug(f"registering callback {callback.__name__} to event type {event_type}")

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

        self._logger.debug("began listening!")

        for slack_event in self._slackSocket.events():
            if slack_event:
                if slack_event.event and "bot_id" not in slack_event.event:  # We don't reply to bots
                    request = SlackRequest(self._slacker, slack_event)
                    self.route_request_to_notify(request)

            time.sleep(READ_WEBSOCKET_DELAY)

        self._logger.debug("Keyboard interrupt received. Gracefully shutting down")
        sys.exit(0)

    def start(self):
        """
        Connect the slack bot to the chatroom and begin listening to channel
        """

        ok = self._slacker.rtm.start().body["ok"]

        if ok:
            self._logger.debug("started!")
            self.listen()
        else:
            self._logger.error("Connection failed. Are you connected to the internet? Potentially invalid Slack token? "
                               "Check environment variable and \"SLACK_BOT_TOKEN\"")

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

        for private_channel in private_channels:
            private_channels.append(private_channel["id"])

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

        users_list = self._slacker.users.list()

        for user in users_list.body["members"]:
            if user["id"] == user_id:
                self._logger.debug(f"converted {user_id} to {user['name']}")
                return user["name"]

        self._logger.warning(f"could not convert user id {user_id} to a name")
