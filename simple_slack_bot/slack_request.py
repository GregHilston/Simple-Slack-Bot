class SlackRequest(object):
    """
    Extracts commonly used information from a SlackClient dictionary for easy
    access. Also allows users to write messages, upload content and gain access
    to the underlying SlackClient
    """

    def __init__(self, slacker, slack_event):
        self._slacker = slacker
        self._slack_event = slack_event


    @property
    def type(self):
        return self._slack_event.event["type"]


    @property
    def channel(self):
        channel = ""

        if "channel" in self._slack_event.event:
            channel = self._slack_event.event["channel"]

        return channel


    @property
    def message(self):
        return self._slack_event.event["text"]


    def write(self, content, channel=None):
        """
        Writes the content to the channel

        :param content: The text you wish to send
        :param channel: By default send to same channel request came from
        :param kwargs: any extra arguments you want to pass to chat.postMessage
                       slack API
        """

        if channel is None and self._slack_event:
            channel = self.channel
        
        print(f"writing {content} to {channel}")

        self._slacker.chat.post_message(channel, content)

        print(f"wrote {content} to {channel}")
