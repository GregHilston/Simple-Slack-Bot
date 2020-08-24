class MockPythonSlackclient:
    def __init__(
        self,
        injectable_bool=None,
        injectable_public_channels=[],
        injectable_private_channels=[],
        injectable_user_ids=[],
        injectable_user_names=[],
        injectable_channel_names=[],
        injectable_chat_postMessage_exception=None
    ):
        self.injectable_bool = injectable_bool
        self.injectable_channel_names = injectable_channel_names
        self.injectable_public_channels = injectable_public_channels
        self.injectable_private_channels = injectable_private_channels
        self.injectable_user_ids = injectable_user_ids
        self.injectable_user_names = injectable_user_names
        self.injectable_chat_postMessage_exception = injectable_chat_postMessage_exception

    def rtm_start(self):
        return self.injectable_bool

    def channels_list(self):
        return {
            "channels": [
                {"id": channel_id, "name": channel_name, "members": self.injectable_user_names}
                for channel_id, channel_name, member in zip(
                    self.injectable_public_channels,
                    self.injectable_channel_names,
                    self.injectable_user_names,
                )
            ]
        }

    def groups_list(self):
        return {"groups": [{"id": value} for value in self.injectable_private_channels]}

    def users_list(self):
        return {
            "members": [
                {"id": id, "name": name}
                for id, name in zip(self.injectable_user_ids, self.injectable_user_names)
            ]
        }

    def chat_postMessage(self, channel, text):
        self.was_chat_postMessage_called = True
        self.channel = channel
        self.text = text

        if self.injectable_chat_postMessage_exception:
            print("AH")
            raise self.injectable_chat_postMessage_exception
