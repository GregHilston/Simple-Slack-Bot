import time, os
from slackclient import SlackClient


class SimpleSlackBot:
    def __init__(self):
        self._BOT_ID = os.environ.get("BOT_ID")
        self._SLACK_TOKEN = os.environ.get("SLACK_BOT_TOKEN")
        self._slack_client = SlackClient(self._SLACK_TOKEN)
        self._observer_callbacks = []


    def start(self):
        """
        Connect the slack bot to the chatroom and begin listening to channel
        """

        ret = self._slack_client.rtm_connect()

        if ret:
            print("{} started and running!".format(self._BOT_ID))
            self.listen()
        else:
            print("ret {}".format(ret))
            print("Connection failed. Are you connected to the internet?"
                  " Potentially invalid Slack token or bot ID? Check"
                  " environment variables.ch")


    def listen(self):
        """
        Listens forever, updating on content
        """

        READ_WEBSOCKET_DELAY = 1 # 1 second delay between reading from firehose

        while True:
            json_list = self._slack_client.rtm_read()

            if json_list and len(json_list) > 0:
                for dictionary in json_list:
                    if dictionary and str(dictionary["type"]) == "message":
                        if "bot_id" in dictionary:
                            continue
                        self.update(dictionary)

            time.sleep(READ_WEBSOCKET_DELAY)


    def register(self, callback):
        """
        Registers the observer to receive updates from the observable
        """

        if callback not in self._observer_callbacks:
            self._observer_callbacks.append(callback)


    def update(self, dictionary):
        """
        Notifies observers of the dictionary
        """

        for callback in self._observer_callbacks:
            reply = callback(dictionary)

            if reply:
                self.write(dictionary, reply)


    def write(self, dictionary, content):
        """
        Writes the content to the channel
        """

        print(dictionary)
        print("content")

        self._slack_client.api_call("chat.postMessage", channel=dictionary["channel"], text=content, as_user=True)
