import unittest
from simple_slack_bot.simple_slack_bot import SimpleSlackBot
from simple_slack_bot.slack_request import SlackRequest
from slacksocket.models import SlackEvent


class TestSimpleSlackBot(unittest.TestCase):
    def setUp(self):
        self.sut = SimpleSlackBot(slack_bot_token="MOCK BOT TOKEN")

    def tearDown(self):
        self.sut = None

    def test_get_slacker(self):
        # Given
        mock_slacker = object
        self.sut._slacker = mock_slacker

        # When
        retrieved_slacker = self.sut.get_slacker()

        # Then
        self.assertEqual(mock_slacker, retrieved_slacker, "The retrieved_slacker should be the one we set in Given")

    def test_get_slack_socket(self):
        # Given
        mock_slack_socket = object
        self.sut._slackSocket = mock_slack_socket

        # When
        retrieved_slack_socket = self.sut.get_slack_socket()

        # Then
        self.assertEqual(mock_slack_socket, retrieved_slack_socket, "The retrieved_slack_socket should be the one we set in Given")

class ParametrizedTestCase(unittest.TestCase):
    """ TestCase classes that want to be parametrized should
        inherit from this class.

        From: https://eli.thegreenplace.net/2011/08/02/python-unit-testing-parametrized-test-cases
    """
    def __init__(self, methodName='runTest', param=None):
        super(ParametrizedTestCase, self).__init__(methodName)
        self.param = param

    @staticmethod
    def parametrize(testcase_klass, param=None):
        """ Create a suite containing all tests taken from the given
            subclass, passing them the parameter 'param'.
        """
        testloader = unittest.TestLoader()
        testnames = testloader.getTestCaseNames(testcase_klass)
        suite = unittest.TestSuite()
        for name in testnames:
            suite.addTest(testcase_klass(name, param=param))
        return suite


class TestSimpleSlackBotParameterized(ParametrizedTestCase):
    def setUp(self):
        self.sut = SimpleSlackBot(slack_bot_token="MOCK BOT TOKEN")

    def tearDown(self):
        self.sut = None

    def test_register_actually_registers(self):
        # Given

        # When
        @self.sut.register(self.param)
        def mock_function():
            print("Mock function")

        # Then
        self.assertTrue(len(self.sut._registrations) == 1, "We only registered one function, therefore the count should be 1")
        self.assertTrue(len(self.sut._registrations[self.param]) == 1, "We only registered one function of this type, therefore the count should be 1")

    def test_route_request_to_callbacks(self):
        # Given
        registered_callback_was_called = False

        @self.sut.register(self.param)
        def mock_function(mock_slack_request):
            nonlocal registered_callback_was_called
            registered_callback_was_called = True

        # When
        self.sut.route_request_to_callbacks(SlackRequest(None, SlackEvent({"type": self.param})))

        # Then
        self.assertTrue(registered_callback_was_called, "We registered a function of this type and triggered it, so it should be called")


# initialize the test suite
suite = unittest.TestSuite()

# add non-parameterized tests
suite.addTest(unittest.makeSuite(TestSimpleSlackBot))

# add parameterized tests
SLACK_RTM_EVENTS = ['accounts_changed', 'app_mention', 'app_rate_limited', 'app_uninstalled', 'bot_added', 'bot_changed', 'channel_archive', 'channel_created', 'channel_deleted', 'channel_history_changed', 'channel_joined', 'channel_left', 'channel_marked', 'channel_rename', 'channel_unarchive', 'commands_changed', 'dnd_updated', 'dnd_updated_user', 'email_domain_changed', 'emoji_changed', 'file_change', 'file_comment_added', 'file_comment_deleted', 'file_comment_edited', 'file_created', 'file_deleted', 'file_public', 'file_shared', 'file_unshared', 'goodbye', 'grid_migration_finished', 'grid_migration_started', 'group_archive', 'group_close', 'group_deleted', 'group_history_changed', 'group_joined', 'group_left', 'group_marked', 'group_open', 'group_rename', 'group_unarchive', 'hello', 'im_close', 'im_created', 'im_history_changed', 'im_marked', 'im_open', 'link_shared', 'manual_presence_change', 'member_joined_channel', 'member_left_channel', 'message', 'message.app_home', 'message.channels', 'message.groups', 'message.im', 'message.mpim', 'pin_added', 'pin_removed', 'pref_change', 'presence_change', 'presence_query', 'presence_sub', 'reaction_added', 'reaction_removed', 'reconnect_url', 'resources_added', 'resources_removed', 'scope_denied', 'scope_granted', 'star_added', 'star_removed', 'subteam_created', 'subteam_members_changed', 'subteam_self_added', 'subteam_self_removed', 'subteam_updated', 'team_domain_change', 'team_join', 'team_migration_started', 'team_plan_change', 'team_pref_change', 'team_profile_change', 'team_profile_delete', 'team_profile_reorder', 'team_rename', 'tokens_revoked', 'url_verification', 'user_change', 'user_resource_denied', 'user_resource_granted', 'user_resource_removed', 'user_typing']
for slack_rtm_event in SLACK_RTM_EVENTS:
    suite.addTest(ParametrizedTestCase.parametrize(TestSimpleSlackBotParameterized, param=slack_rtm_event))

# initialize a runner, pass it your suite and run it
runner = unittest.TextTestRunner(verbosity=3)
result = runner.run(suite)


if __name__ == '__main__':
    unittest.main()
