import logging

logger = logging.getLogger(__name__)


class SlackRequest(object):
    """Extracts commonly used information from a SlackClient dictionary for easy access. Also allows users to write
    messages, upload content and gain access to the underlying SlackClient
    """

    def __init__(self, slacker, slack_event):
        """Initializes a SlackRequest

        :param slacker: the Slacker object for this specific SlackRequest
        :param slack_event: the SlackEvent for this specific SlackRequest
        """
        self._slacker = slacker
        self._slack_event = slack_event

    @property
    def type(self):
        """Gets the type of event from the underlying SlackEvent

        :return: the type of event, if there is one
        """

        if "type" in self._slack_event.event:
            return self._slack_event.event["type"]

    @property
    def channel(self):
        """Gets the channel from the underlying SlackEvent
        Note: This can be an empty String. For example, this will be an empty String for the 'Hello' event.

        :return: the channel this SlackEvent originated from, if there is one
        """

        channel = ""

        if "channel" in self._slack_event.event:
            channel = self._slack_event.event["channel"]

        return channel

    @property
    def message(self):
        """Gets the underlying message from the SlackEvent
        Note: This can be an empty String. For example, this will be an empty String for the 'message_changed' event.

        :return: the message this SlackEvent came with, if there is one
        """

        if "text" in self._slack_event.event:
            return self._slack_event.event["text"]

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

        try:
            self._slacker.chat.post_message(channel, content)
        except Exception as e:
            logger.warning(e)

    def __str__(self):
        """Generates the String representation of a SlackRequest

        :return: the String representation of a SlackRequest
        """

        return str(self._slack_event.json)
