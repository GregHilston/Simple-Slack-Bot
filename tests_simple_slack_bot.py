import unittest
from simple_slack_bot.simple_slack_bot import SimpleSlackBot


class TestSimpleSlackBot(unittest.TestCase):
    def setUp(self):
        self.sut = SimpleSlackBot(slack_bot_token="MOCK BOT TOKEN")

    def tearDown(self):
        self.sut = None

    def test_register_actually_registers(self):
        # Given

        # When
        @self.sut.register("hello")
        def mock_function():
            print("Mock function")

        # Then
        self.assertTrue(len(self.sut._registrations) == 1)
        self.assertTrue(len(self.sut._registrations["hello"]) == 1)


if __name__ == '__main__':
    unittest.main()