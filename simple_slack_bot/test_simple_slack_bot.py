import unittest
from simple_slack_bot import SimpleSlackBot


class TestSimpleSlackBot(unittest.TestCase):
    def setUp(self):
        self._simple_slack_bot = SimpleSlackBot()


if __name__ == '__main__':
    unittest.main()
