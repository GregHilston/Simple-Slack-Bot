import unittest
from simple_slack_bot.simple_slack_bot import SimpleSlackBot


class TestSimpleSlackBot(unittest.TestCase):
    def setUp(self):
        print("setUp")
        self.sut = SimpleSlackBot()

    def tearDown(self):
        print("tearDown")

        self.sut.dispose()
        self.sut = SimpleSlackBot()

    def test_register_actually_registers(self):
        # Given

        # When
        @self.sut.register("hello")
        def mock_function():
            print("Mock fuction")

        # Then
        self.assertTrue(len(self.sut._registrations) == 99)