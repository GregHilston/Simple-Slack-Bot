"""Please refer to the documentation provided in the README.md.
which can be found at the PyPI URL: https://pypi.org/project/simple-slack-bot/
"""


import itertools
import logging
import logging.config
import os
import sys
import time
import traceback
import typing
from logging import StreamHandler

import slacksocket.errors  # type: ignore
from slack import WebClient
from slacksocket import SlackSocket  # type: ignore
from slacksocket.models import SlackEvent  # type: ignore

from .slack_request import SlackRequest

logger = logging.getLogger(__name__)


class SimpleSlackBot:
    """Simplifie interacting with the Slack API.

    Allows users to register functions to specific events, get those functions
    called when those specific events are triggered and run their business code
    """

    KEYBOARD_INTERRUPT_EXCEPTION_LOG_MESSAGE = "KeyboardInterrupt exception caught."
    SYSTEM_INTERRUPT_EXCEPTION_LOG_MESSAGE = "SystemExit exception caught."

    @staticmethod
    def peek(
        iterator: typing.Iterator,
    ) -> typing.Union[None, typing.Tuple[typing.Any, typing.Iterator]]:
        """Allow us to look at the next yield in an Iterator.

        From: https://stackoverflow.com/a/664239/1983957

        :param iterator: some Iterator to peek at
        :return: the first and rest of the yielded items
        """

        try:
            first = next(iterator)
        except StopIteration:
            return None
        return first, itertools.chain([first], iterator)

    def __init__(self, slack_bot_token: str = None, debug: bool = False):
        """Initialize our Slack bot and slack bot token.

        Will exit if the required environment variable is not set.

        :param slack_bot_token: The token given by Slack for API authentication
        :param debug: Whether or not to use default a Logging config
        """

        # fetch a slack_bot_token first checking params, then environment variable otherwise
        # raising a SystemExit exception as this is required for execution
        if slack_bot_token is None:
            self._slack_bot_token = os.environ.get("SLACK_BOT_TOKEN")
        else:
            self._slack_bot_token = slack_bot_token
        if self._slack_bot_token is None or self._slack_bot_token == "":
            sys.exit(
                "ERROR: SLACK_BOT_TOKEN not passed to constructor or set as environment variable"
            )

        if debug:
            # enable logging additional debug logging
            logger.addHandler(StreamHandler())
            logger.setLevel(logging.DEBUG)

        logger.info("initialized. Ready to connect")

    def connect(self):
        """Connect to underlying SlackSocket.

        Additionally stores conections for future usage.
        """
        # Disable all the attribute-defined-out-init in this function
        # pylint: disable=attribute-defined-outside-init

        logger.info("Connecting...")

        self._python_slackclient = WebClient(self._slack_bot_token)
        self._slack_socket = SlackSocket(self._slack_bot_token)
        self._bot_id = self._python_slackclient.auth_test()["bot_id"]

        logger.info(
            "Connected. Set bot id to %s with name %s",
            self._bot_id,
            self.helper_user_id_to_user_name(self._bot_id),
        )

    def register(self, event_type: str) -> typing.Callable[..., typing.Any]:
        """Register a callback function to a a event type.

        All supported even types are defined here https://api.slack.com/events-api

        :param event_type: the type of the event to register
        :return: reference to wrapped function
        """

        def function_wrapper(callback: typing.Callable):
            """Register event before executing wrapped function, referred to as callback.

            :param callback: function to execute after runnign wrapped code
            """
            # Disable all the attribute-defined-out-init in this function
            # pylint: disable=attribute-defined-outside-init

            # first time initialization
            if not hasattr(self, "_registrations"):
                self._registrations: typing.Dict[str, typing.List[typing.Callable]] = {}

            if event_type not in self._registrations:
                # first registration of this type
                self._registrations[event_type] = []
            self._registrations[event_type].append(callback)

        return function_wrapper

    def route_request_to_callbacks(self, request: SlackRequest):
        """Route the request to the correct notify.

        :param request: request to be routed
        """
        logger.info(
            "received an event of type %s and slack event type of %s with content %s",
            request.type,
            request.slack_event.type,
            request,
        )

        # we ignore subtypes to ensure thread messages don't go to the channel as well, as two events are created
        # i'm totally confident this will have unexpected consequences but have not discovered any at the time of
        # writing this
        if request.type in self._registrations and request.subtype is None:
            for callback in self._registrations[request.type]:
                try:
                    callback(request)
                except Exception:  # pylint: disable=broad-except
                    logger.exception(
                        "exception processing event %s . Exception %s",
                        request.type,
                        traceback.format_exc(),
                    )

    def extract_slack_socket_response(self) -> typing.Union[SlackEvent, None]:
        """Extract a useable response from the underlying _slack_socket.

        Catch all SlackSocket exceptions except forExitError, treating those as warnings.
        """
        try:
            return self.peek(self._slack_socket.events())
        except (
            slacksocket.errors.APIError,
            slacksocket.errors.ConfigError,
            slacksocket.errors.APINameError,
            slacksocket.errors.ConnectionError,
            slacksocket.errors.TimeoutError,
        ):
            logging.warning(
                "Unexpected exception caught, but we will keep listening. Exception: %s",
                traceback.format_exc(),
            )
            return None  # ensuring the loop continues and execution ends

    def listen(self):
        """Listen forever for Slack events, triggering appropriately callbacks when respective events are received.

        Catches and logs all Exceptions except for KeyboardInterrupt or SystemExit, which gracefully shuts down program.

        The following function is crucial to Simple Slack Bot and looks a little messy. Since most of Simple Slack Bot's
        time is spent blocked on waiting for events from SlackSocket, a solution was needed to deal with this. Otherwise
        our application would not respond to a request from the user to stop the program with a CTRL + C.
        """

        read_websocket_delay = 1  # 1 second delay between reading from fire hose
        running = True

        logger.info("began listening!")

        # required to continue to run after experiencing an unexpected exception
        while running:
            response = None

            try:
                while response is None:
                    response = self.extract_slack_socket_response()
            except slacksocket.errors.ExitError:
                logging.info(self.KEYBOARD_INTERRUPT_EXCEPTION_LOG_MESSAGE)
                running = False
                break  # ensuring the loop stops and execution ceases

            slack_event, _ = response
            try:
                self.route_request_to_callbacks(SlackRequest(self._python_slackclient, slack_event))

                time.sleep(read_websocket_delay)
            except Exception:  # pylint: disable=broad-except
                logging.warning(
                    "Unexpected exception caught, but we will keep listening. Exception: %s",
                    traceback.format_exc(),
                )
                continue  # ensuring the loop continues

    logger.info("stopped listening!")

    def start(self):
        """Connect the Slack bot to the chatroom and begin listening."""

        self.connect()
        ok_reponse = self._python_slackclient.rtm_start()

        if ok_reponse:
            logger.info("started!")
            self.listen()
        else:
            logger.error(
                "Connection failed. Are you connected to the internet? Potentially invalid Slack token? "
                'Check environment variable and "SLACK_BOT_TOKEN"'
            )

        logger.info("stopped!")

    def helper_get_public_channel_ids(self) -> typing.List[str]:
        """Get all public channel ids.

        :return: list of public channel ids
        """

        public_channel_ids = []

        if self._python_slackclient and self._python_slackclient.channels_list():
            public_channels = self._python_slackclient.channels_list()["channels"]
            for channel in public_channels:
                public_channel_ids.append(channel["id"])

            if len(public_channel_ids) == 0:
                logger.warning("got no public channel ids")
            else:
                logger.debug("got public channel ids %s", public_channel_ids)

        return public_channel_ids

    def helper_get_private_channel_ids(self) -> typing.List[str]:
        """Get all private channel ids.

        :return: list of private channel ids
        """

        private_channel_ids: typing.List[str] = []

        for private_channel in self._python_slackclient.groups_list()["groups"]:
            private_channel_ids.append(private_channel["id"])

        if len(private_channel_ids) == 0:
            logger.warning("got no private channel ids")
        else:
            logger.debug("got private channel ids %s", private_channel_ids)

        return private_channel_ids

    def helper_get_user_ids(self) -> typing.List[str]:
        """Get all user ids.

        :return: list of user ids
        """

        user_ids = []

        for user in self._python_slackclient.users_list()["members"]:
            user_ids.append(user["id"])

        if len(user_ids) == 0:
            logger.warning("got no user ids")
        else:
            logger.debug("got user ids %s", user_ids)

        return user_ids

    def helper_get_user_names(self) -> typing.List[str]:
        """Get all user names.

        :return: list of user names
        """

        user_names = []

        for user in self._python_slackclient.users_list()["members"]:
            user_names.append(user["name"])

        if len(user_names) == 0:
            logger.warning("got no user names")
        else:
            logger.debug("got user names %s", user_names)

        return user_names

    def helper_get_users_in_channel(self, channel_id: str) -> typing.List[str]:
        """Get all users in a given channel id.

        :param channel_id: channel id to get all user ids in it
        :return: list of user ids
        """

        user_ids = []

        for channel in self._python_slackclient.channels_list()["channels"]:
            if channel["id"] == channel_id:
                for user_id in channel["members"]:
                    user_ids.append(user_id)

        if len(user_ids) == 0:
            logger.warning("got no user ids for channel %s", channel_id)
        else:
            logger.debug("got user ids %s", user_ids)

        return user_ids

    def helper_channel_name_to_channel_id(self, name: str) -> typing.Union[str, None]:
        """Convert a channel name to its respected channel id.

        :param name: name of channel to convert to id
        :return: id representation of original channel name
        """

        for channel in self._python_slackclient.channels_list()["channels"]:
            if channel["name"] == name:
                logger.debug("converted %s to %s", channel["name"], channel["id"])
                return channel["id"]

        logger.warning("could not convert channel name %s to an id", name)
        return None

    def helper_user_name_to_user_id(self, name: str) -> typing.Union[str, None]:
        """Convert a user name to its respected user id.

        :param name: name of user to convert to id
        :return: id representation of original user name
        """

        for user in self._python_slackclient.users_list()["members"]:
            if user["name"] == name:
                logger.debug("converted %s to %s", name, user["id"])
                return user["id"]

        logger.warning("could not convert user name %s to a user id", name)
        return None

    def helper_channel_id_to_channel_name(self, channel_id: str) -> typing.Union[str, None]:
        """Convert a channel id to its respected channel name.

        :param channel_id: id of channel to convert to name
        :return: name representation of original channel id
        """

        for channel in self._python_slackclient.channels_list()["channels"]:
            if channel["id"] == channel_id:
                logger.debug("converted %s to %s", channel_id, channel["name"])
                return channel["name"]

        logger.warning("could not convert channel id %s to a name", channel_id)
        return None

    def helper_user_id_to_user_name(self, user_id: str) -> typing.Union[str, None]:
        """Convert a user id to its respected user name.

        :param user_id: id of user to convert to name
        :return: name representation of original user id
        """

        for user in self._python_slackclient.users_list()["members"]:
            if user["id"] == user_id:
                logger.debug("converted %s to %s", user_id, user["name"])
                return user["name"]

        logger.warning("could not convert user id %s to a name", user_id)
        return None
