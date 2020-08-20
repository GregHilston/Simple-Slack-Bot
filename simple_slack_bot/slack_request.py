"""
Please refer to the documentation provided in the README.md.
which can be found at the PyPI URL: https://pypi.org/project/simple-slack-bot/
"""


import logging
import traceback

logger = logging.getLogger(__name__)


class SlackRequest:
    """Extracts commonly used information from a SlackClient dictionary for easy access. Also allows users to write
    messages, upload content and gain access to the underlying SlackClient
    """

    def __init__(self, python_slackclient, slack_event):
        """Initializes a SlackRequest

        :param WebClient: the WebClient object for this specific SlackRequest
        :param slack_event: the SlackEvent for this specific SlackRequest
        """
        self._python_slackclient = python_slackclient
        self.slack_event = slack_event

    @property
    def type(self):
        """Gets the type of event from the underlying SlackEvent

        :return: the type of event, if there is one
        """

        if "type" in self.slack_event:
            return self.slack_event["type"]

        logger.warning("could not find type for slack_event")
        return None

    @property
    def subtype(self):
        """Gets the subtype of event from the underlying SlackEvent

        :return: the subtype of event, if there is one
        """

        if "subtype" in self.slack_event:
            return self.slack_event["subtype"]

        logger.warning("could not find subtype for slack_event")
        return None

    @property
    def channel(self):
        """Gets the channel from the underlying SlackEvent
        Note: This can be an empty String. For example, this will be an empty String for the 'Hello' event.

        :return: the channel this SlackEvent originated from, if there is one
        """

        channel = ""

        if "channel" in self.slack_event:
            channel = self.slack_event["channel"]

        return channel

    @property
    def thread_ts(self):
        """Gets the thread_ts from the underlying SlackEvent.
        Note: This can be an empty String. For example, this will be an empty String when a message was not sent in a thread.

        :return: the thread_ts this SlackEvent originated from, if there is one
        """

        thread_ts = ""
        if "thread_ts" in self.slack_event:
            thread_ts = self.slack_event["thread_ts"]

        return thread_ts

    @property
    def message(self):
        """Gets the underlying message from the SlackEvent
        Note: This can be an empty String. For example, this will be an empty String for the 'message_changed' event.

        :return: the message this SlackEvent came with, if there is one
        """

        if "text" in self.slack_event:
            return self.slack_event["text"]

        logger.warning("could not find text for slack_event")
        return None

    def write(self, content, channel=None):
        """
        Writes the content to the channel

        :param content: The text you wish to send
        :param channel: By default send to same channel request came from, if any
        """

        if channel is None and self.channel != "":
            channel = self.channel
        else:
            logger.warning("no channel provided by developer or respective slack event")

        # optional arguments
        kwargs = {}

        # if the message we're replying to came from a thread, we'll grab the thread_ts
        # so we can reply in said thread
        if "thread_ts" in self.slack_event:
            kwargs["thread_ts"] = self.slack_event["thread_ts"]
        try:
            self._python_slackclient.chat_postMessage(
                channel=channel, text=content, **kwargs
            )
        except Exception:  # pylint: disable=broad-except
            logging.warning(
                "Unexpected exception caught, but we will keep listening. Exception: %s",
                traceback.format_exc(),
            )
            logger.warning(traceback.format_exc())

    def __str__(self):
        """Generates the String representation of a SlackRequest

        :return: the String representation of a SlackRequest
        """

        return str(self.slack_event.json)
