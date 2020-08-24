"""
Please refer to the documentation provided in the README.md.

which can be found at the PyPI URL: https://pypi.org/project/simple-slack-bot/
"""


import logging
import traceback
import typing

from slack import WebClient
from slacksocket.models import SlackEvent  # type: ignore

logger = logging.getLogger(__name__)


class SlackRequest:
    """Extract commonly used information from a SlackClient dictionary for easy access.

    Also allows users to write messages, upload content and gain access to the underlying SlackClient
    """

    def __init__(self, python_slackclient: WebClient, slack_event: SlackEvent):
        """Initialize a SlackRequest.

        :param python_slackclient: the WebClient object for this specific SlackRequest
        :param slack_event: the SlackEvent for this specific SlackRequest
        """
        self._python_slackclient = python_slackclient
        self.slack_event = slack_event

    def get(self, key: str, default_value: typing.Any = None) -> typing.Any:
        """Get value for given key if found otherwise return default value.

        :param key: The key we're looking for
        :param default_value: What to return if we can't find a value for this key
        :return: The found value or default value if not found
        """
        if key in self.slack_event:
            return self.slack_event[key]

        logger.warning("could not find %s for slack_event", key)
        return default_value

    @property
    def type(self) -> typing.Union[str, None]:
        """Get the type of event from the underlying SlackEvent.

        :return: the type of event, if there is one
        """

        return self.get("type")

    @property
    def subtype(self) -> typing.Union[str, None]:
        """Get the subtype of event from the underlying SlackEvent.

        :return: the subtype of event, if there is one
        """

        return self.get("subtype")

    @property
    def channel(self) -> typing.Union[str, None]:
        """Get the channel from the underlying SlackEvent.

        Note: This can be an empty String. For example, this will be an empty String for the 'Hello' event.

        :return: the channel this SlackEvent originated from, if there is one
        """

        return self.get("channel")

    @property
    def thread_ts(self) -> str:
        """Get the thread_ts from the underlying SlackEvent.

        Note: This can be an empty String. For example, this will be an empty String when a message was not sent in a thread.

        :return: the thread_ts this SlackEvent originated from, if there is one
        """

        thread_ts = ""
        if "thread_ts" in self.slack_event:
            thread_ts = self.slack_event["thread_ts"]

        return thread_ts

    @property
    def message(self) -> typing.Union[str, None]:
        """Get the underlying message from the SlackEvent.

        Note: This can be an empty String. For example, this will be an empty String for the 'message_changed' event.

        :return: the message this SlackEvent came with, if there is one
        """

        if "text" in self.slack_event:
            return self.slack_event["text"]

        logger.warning("could not find text for slack_event")
        return None

    def write(self, content: str, channel: typing.Optional[str] = None):
        """Write the content to the channel.

        :param content: The text you wish to send
        :param channel: By default send to same channel request came from, if any
        :raises Exception: If channel cannot be determined
        """

        if channel is None and self.channel != "":
            channel = self.channel
        else:
            logger.warning("no channel provided by developer or respective slack event")

        # optional promotion
        if channel is None:
            raise Exception("Unable to determine which channel to write to")
        actual_channel: str = channel

        # optional arguments
        kwargs = {}

        # if the message we're replying to came from a thread, we'll grab the thread_ts
        # so we can reply in said thread
        if "thread_ts" in self.slack_event:
            kwargs["thread_ts"] = self.slack_event["thread_ts"]
        try:
            self._python_slackclient.chat_postMessage(
                channel=actual_channel, text=content, **kwargs
            )
        except Exception:  # pylint: disable=broad-except
            logging.warning(
                "Unexpected exception caught, but we will keep listening. Exception: %s",
                traceback.format_exc(),
            )
            logger.warning(traceback.format_exc())

    def __str__(self) -> str:
        """
        Generate the String representation of a SlackRequest.

        :return: the String representation of a SlackRequest
        """

        return str(self.slack_event.json)
