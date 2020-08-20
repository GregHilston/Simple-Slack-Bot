import logging
import os


import pytest
import slacksocket.errors  # type: ignore
from slack import WebClient
from slacksocket.models import SlackEvent  # type: ignore

from simple_slack_bot.simple_slack_bot import SimpleSlackBot, SlackRequest


class MockIterator:
    def __init__(self):
        self.injectable_yield = None
        self.raiseable_exception = None

    def __iter__(self):
        return self

    def __next__(self):
        if self.raiseable_exception:
            raise self.raiseable_exception

        return self.injectable_yield


class MockSlackSocket:
    def events(self):
        return iter(self.mock_iterator)


def test_init_raises_systemexit_exception_when_not_passed_slack_bot_token_or_has_environment_variable_to_fall_back_on():
    # Given
    # unset any state that may have been set by user or other tests prior
    if "SLACK_BOT_TOKEN" in os.environ:
        temp_slack_bot_token = os.environ["SLACK_BOT_TOKEN"]
        del os.environ["SLACK_BOT_TOKEN"]

    # When

    with pytest.raises(SystemExit):
        sut = SimpleSlackBot()

    # Then
    # reset environment variable if it was unset
    if "temp_slack_bot_token" in locals():
        os.environ["SLACK_BOT_TOKEN"] = temp_slack_bot_token


def test_init_prefers_parameters_over_environment_variables():
    # Given
    slack_bot_token = "token1"
    os.environ["SLACK_BOT_TOKEN"] = "token2"

    # When
    sut = SimpleSlackBot(slack_bot_token=slack_bot_token)

    # Then
    assert (
        sut._SLACK_BOT_TOKEN == slack_bot_token
    ), "Should prioritize this value when storing over environment variable"
    assert (
        sut._SLACK_BOT_TOKEN != os.environ["SLACK_BOT_TOKEN"]
    ), "Should not use this value, priorizing the paramter"


def test_register_actually_registers():
    # Given
    sut = SimpleSlackBot(slack_bot_token="MOCK BOT TOKEN")

    # When
    @sut.register("message")
    def mock_function():
        print("Mock function")

    # Then
    assert (
        len(sut._registrations) == 1
    ), "We only registered one function, therefore the count should be"
    assert (
        len(sut._registrations["message"]) == 1
    ), "We only registered one function of this type, therefore the count should be 1"


def test_route_request_to_callbacks_routes_correct_type_to_correct_callback():
    # Given
    class Monitor:
        was_called = False

        def monitor_if_called(self, request):
            Monitor.was_called = True

    mock_slack_event = SlackEvent({"type": "message"})
    mock_slackrequest = SlackRequest(
        python_slackclient=None, slack_event=mock_slack_event
    )
    sut = SimpleSlackBot(slack_bot_token="Mock slack bot token")
    monitor = Monitor()
    sut._registrations = {}
    sut._registrations["message"] = [monitor.monitor_if_called]

    # When
    sut.route_request_to_callbacks(mock_slackrequest)

    # Then
    assert Monitor.was_called is True


def test_listen_stops_listening_when_slack_socket_keyboard_interrupt_exception_occurs(caplog):
    # Given
    mock_iterator = MockIterator()
    mock_iterator.raiseable_exception = slacksocket.errors.ExitError

    mock_slack_socket = MockSlackSocket()
    mock_slack_socket.mock_iterator = mock_iterator

    sut = SimpleSlackBot("mock slack bot token")
    sut._slackSocket = mock_slack_socket

    # When
    with caplog.at_level(logging.INFO):
        sut.listen()

    # Then
    assert SimpleSlackBot.KEYBOARD_INTERRUPT_EXCEPTION_LOG_MESSAGE in caplog.text


# Since this test uses an infinite loop and we're testing if that loop isn't
# killed by sending an APIError we'll use a timeout. Additionally we have to use
# the method=Thread as this test is dependent on the SIGALRM signal.
@pytest.mark.timeout(1, method="thread")
def test_listen_stops_listening_when_unexpected_exception_occurs(caplog):
    # Given
    mock_iterator = MockIterator()
    mock_iterator.raiseable_exception = slacksocket.errors.APIError

    mock_slack_socket = MockSlackSocket()
    mock_slack_socket.mock_iterator = mock_iterator

    sut = SimpleSlackBot("mock slack bot token")
    sut._slackSocket = mock_slack_socket

    # When
    with caplog.at_level(logging.INFO):
        sut.listen()

    # Then
    assert "Unexpected" in caplog.text


def test_start_calls_listen_if_slackclient_rtm_has_valid_ok():
    # TODO
    pass


def test_start_errors_out_if_slackclient_rtm_has_invalid_ok():
    # TODO
    pass


def test_listen_calls_route_request_to_callbacks_when_valid_request():
    pass
    # Given

    # When
    # sut.listen()

    # Then
