import os
import sys
import time
import logging
import logging.config
import traceback
import itertools
from logging import StreamHandler
from slacker import Slacker
from slacksocket import SlackSocket
from .slack_request import SlackRequest

logger = logging.getLogger(__name__)


class SimpleSlackBot:
    """Simplifies interacting with the Slack API. Allows users to register functions to specific events, get those
    functions called when those specific events are triggered and run their business code
    """

    KEYBOARD_INTERRUPT_EXCEPTION_LOG_MESSAGE = "KeyboardInterrupt exception caught."
    SYSTEM_INTERRUPT_EXCEPTION_LOG_MESSAGE = "SystemExit exception caught."

    @staticmethod
    def peek(iterable):
        """Allows us to look at the next yield in an Iterable.
        From: https://stackoverflow.com/a/664239/1983957

        :param iterable: some Iterable to peek at
        :return: the first and rest of the yielded items
        """

        try:
            first = next(iterable)
        except StopIteration:
            return None
        return first, itertools.chain([first], iterable)

    @staticmethod
    def log_gracefully_shutdown(prefix_str):
        """Just a convenient way to log multiple messages in a similar way

        :param prefix_str: String to log in the begging
        :return: None
        """
        logger.info(f"{prefix_str} Gracefully shutting down")

    def __init__(self, debug=False):
        """Initializes our Slack bot and slack bot token. Will exit if the required environment
        variable is not set.

        :param debug: Whether or not to use default a Logging config
        """

        self._SLACK_BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN")
        if self._SLACK_BOT_TOKEN is None:
            sys.exit("ERROR: environment variable SLACK_BOT_TOKEN is not set")

        self._slacker = Slacker(self._SLACK_BOT_TOKEN)
        self._slackSocket = SlackSocket(self._SLACK_BOT_TOKEN, translate=False)
        self._BOT_ID = self._slacker.auth.test().body["user_id"]
        self._registrations = {}  # our dictionary of event_types to a list of callbacks

        if debug:
            # Enable logging for our users
            logger.addHandler(StreamHandler())
            logger.setLevel(logging.DEBUG)

        logger.info(f"set bot id to {self._BOT_ID} with name {self.helper_user_id_to_user_name(self._BOT_ID)}")
        logger.info("initialized")

    def register(self, event_type):
        """Registers a callback function to a a event type. All supported even types are defined here
        https://api.slack.com/events-api

        :param event_type: the type of the event to register
        :return: reference to wrapped function
        """

        def function_wrapper(callback):
            """Registers event before executing wrapped function, referred to as callback

            :param callback: function to execute after runnign wrapped code
            :return: None
            """

            logger.info(f"registering callback {callback.__name__} to event type {event_type}")

            if event_type not in self._registrations:
                self._registrations[event_type] = []  # create an empty list
            self._registrations[event_type].append(callback)

        return function_wrapper

    def route_request_to_callbacks(self, request):
        """Routes the request to the correct notify

        :param request: request to be routed
        :return: None
        """

        logger.info(f"received an event of type {request.type} and slack event {request._slack_event.event}")

        if request.type in self._registrations:
            for callback in self._registrations[request.type]:
                try:
                    callback(request)
                except Exception as ex:
                    logger.exception(f'exception processing event {request.type}')

    def listen(self):
        """Listens forever for Slack events, triggering appropriately callbacks when respective events are received.
        Catches and logs all Exceptions except for KeyboardInterrupt or SystemExit, which gracefully shuts down program.

        The following function is crucial to Simple Slack Bot and looks a little messy. This is do partly to the way
        that our dependency SlackSocket is written. They do not re-raise any caught KeyboardInterrupt exceptions and
        instead we have to infer one was caught based on what their generator returns. This is incredibly unfortunate,
        but this currently works. Since most of Simple Slack Bot's time is spent blocked on waiting for events from
        SlackSocket, a solution was needed to deal with this. Otherwise our application would not respond to a request
        from the user to stop the program with a CTRL + C.
        """

        READ_WEBSOCKET_DELAY = 1  # 1 second delay between reading from fire hose
        running = True

        logger.info("began listening!")

        while running:  # required to continue to run after experiencing an unexpected exception
            res = self.peek(self._slackSocket.events())
            if res is None:
                self.log_gracefully_shutdown(self.KEYBOARD_INTERRUPT_EXCEPTION_LOG_MESSAGE)
                running = False
                break
            else:
                slack_event, mysequence = res

                if slack_event.event and "bot_id" not in slack_event.event:  # We don't reply to bots
                    try:
                        request = SlackRequest(self._slacker, slack_event)
                        self.route_request_to_callbacks(request)

                        time.sleep(READ_WEBSOCKET_DELAY)
                    except KeyboardInterrupt:
                        self.log_gracefully_shutdown(self.KEYBOARD_INTERRUPT_EXCEPTION_LOG_MESSAGE)
                        running = False
                        break
                    except SystemExit:
                        self.log_gracefully_shutdown(self.SYSTEM_INTERRUPT_EXCEPTION_LOG_MESSAGE)
                        running = False
                        break
                    except Exception as e:
                        logging.warning(f"Unexpected exception caught, but we will keep listening. Exception: {e}")
                        logging.warning(traceback.format_stack())
                        continue  # ensuring the loop continues

        logger.info("stopped listening!")

    def start(self):
        """Connect the Slack bot to the chatroom and begin listening
        """

        ok = self._slacker.rtm.start().body["ok"]

        if ok:
            logger.info("started!")
            self.listen()
        else:
            logger.error("Connection failed. Are you connected to the internet? Potentially invalid Slack token? "
                         "Check environment variable and \"SLACK_BOT_TOKEN\"")

        logger.info("stopped!")

    def get_slacker(self):
        """Returns SimpleSlackBot's SlackClient.

        This is useful if you are writing a more advanced bot and want complete access to all SlackClient has to offer.
        """

        return self._slacker

    def get_slack_socket(self):
        """Returns SimpleSlackBot's SlackSocket.

        This is useful if you are writing a more advanced bot and want complete access to all SlackSocket has to offer.
        """

        return self._slackSocket

    def helper_get_public_channel_ids(self):
        """Helper function that gets all public channel ids
        """

        public_channel_ids = []

        public_channels = self._slacker.channels.list().body["channels"]
        for channel in public_channels:
            public_channel_ids.append(channel["id"])

        if len(public_channel_ids) == 0:
            logger.warning("got no public channel ids")
        else:
            logger.debug(f"got public channel ids {public_channel_ids}")

        return public_channel_ids

    def helper_get_private_channel_ids(self):
        """Helper function that gets all private channel ids
        """

        private_channel_ids = []

        private_channels = self._slacker.groups.list().body["groups"]

        for private_channel in private_channels:
            private_channels.append(private_channel["id"])

        if len(private_channel_ids) == 0:
            logger.warning("got no private channel ids")
        else:
            logger.debug(f"got private channel ids {private_channel_ids}")

        return private_channel_ids

    def helper_get_user_ids(self):
        """Helper function that gets all user ids
        """

        user_ids = []

        users = self._slacker.users.list().body["members"]
        for user in users:
            user_ids.append(user["id"])

        if len(user_ids) == 0:
            logger.warning("got no user ids")
        else:
            logger.debug(f"got user ids {user_ids}")

        return user_ids

    def helper_get_user_names(self):
        """Helper function that gets all user names
        """

        user_names = []

        users = self._slacker.users.list().body["members"]
        for user in users:
            user_names.append(user["name"])

        if len(user_names) == 0:
            logger.warning("got no user names")
        else:
            logger.debug(f"got user names {user_names}")

        return user_names

    def helper_get_users_in_channel(self, channel_id):
        """Helper function that gets all users in a given channel id

        :param channel_id: channel id to get all user ids in it
        :return: list of user ids
        """

        user_ids = []

        channels_list = self._slacker.channels.list().body["channels"]
        for channel in channels_list:
            if channel["id"] == channel_id:
                for user_id in channel["members"]:
                    user_ids.append(user_id)

        if len(user_ids) == 0:
            logger.warning(f"got no user ids for channel {channel_id}")
        else:
            logger.debug(f"got user ids {user_ids}")

        return user_ids

    def helper_channel_name_to_channel_id(self, name):
        """Helper function that converts a channel name to its respected channel id

        :param name: name of channel to convert to id
        :return: id representation of original channel name
        """

        channels_list = self._slacker.channels.list().body["channels"]

        for channel in channels_list:
            if channel["name"] == name:
                logger.debug(f"converted {channel['name']} to {channel['id']}")
                return channel["id"]

        logger.warning(f"could not convert channel name {name} to an id")

    def helper_user_name_to_user_id(self, name):
        """Helper function that converts a user name to its respected user id

        :param name: name of user to convert to id
        :return: id representation of original user name
        """

        users = self._slacker.users.list().body["members"]

        for user in users:
            if user["name"] == name:
                logger.debug(f"converted {name} to {user['id']}")
                return user["id"]

        logger.warning(f"could not convert user name {name} to a user id")

    def helper_channel_id_to_channel_name(self, channel_id):
        """Helper function that converts a channel id to its respected channel name

        :param channel_id: id of channel to convert to name
        :return: name representation of original channel id
        """

        channels_list = self._slacker.channels.list().body["channels"]

        for channel in channels_list:
            if channel["id"] == channel_id:
                logger.debug("converted {} to {}".format(channel_id, channel["name"]))
                return channel["name"]

        logger.warning(f"could not convert channel id {channel_id} to a name")

    def helper_user_id_to_user_name(self, user_id):
        """Helper function that converts a user id to its respected user name

        :param user_id: id of user to convert to name
        :return: name representation of original user id
        """

        users_list = self._slacker.users.list()

        for user in users_list.body["members"]:
            if user["id"] == user_id:
                logger.debug(f"converted {user_id} to {user['name']}")
                return user["name"]

        logger.warning(f"could not convert user id {user_id} to a name")
