import os

import pytest

from slack import WebClient
from simple_slack_bot.simple_slack_bot import SimpleSlackBot, SlackRequest
from slacksocket.models import SlackEvent


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
    assert sut._SLACK_BOT_TOKEN == slack_bot_token, "Should prioritize this value when storing over environment variable"
    assert sut._SLACK_BOT_TOKEN != os.environ["SLACK_BOT_TOKEN"], "Should not use this value, priorizing the paramter"


def test_register_actually_registers():
    # Given
    sut = SimpleSlackBot(slack_bot_token="MOCK BOT TOKEN")

    # When
    @sut.register("message")
    def mock_function():
        print("Mock function")

    # Then
    assert len(sut._registrations) == 1, "We only registered one function, therefore the count should be"
    assert len(sut._registrations["message"]) == 1, "We only registered one function of this type, therefore the count should be 1"

def test_route_request_to_callbacks_routes_correct_type_to_correct_callback():
    # Given
    class Monitor:
        was_called = False

        def monitor_if_called(self, request):
            Monitor.was_called = True
    mock_slack_event = SlackEvent({"type": "message"})
    mock_slackrequest = SlackRequest(python_slackclient=None, slack_event=mock_slack_event)
    sut = SimpleSlackBot(slack_bot_token="Mock slack bot token")
    monitor = Monitor()
    sut._registrations = {}
    sut._registrations["message"] = [monitor.monitor_if_called]

    # When
    sut.route_request_to_callbacks(mock_slackrequest)

    # Then
    assert Monitor.was_called == True

@pytest.mark.skip(reason="Currently hanging forever instead of getting into if res is None conditinal")
def test_listen_stops_listening_when_slack_socket_events_returns_none():
    # Given
    class MockSlackSocket:
        def events(self):
            yield None
    mock_slack_socket = MockSlackSocket()
    sut = SimpleSlackBot("mock slack bot token")
    sut._slackSocket = mock_slack_socket

    # When
    sut.listen()

    # Then

def test_listen_calls_route_request_to_callbacks_when_valid_request():
    # TODO
    pass

def test_listen_stops_listening_when_keyboard_interrupt_exception_occurs():
    # TODO
    pass

def test_listen_stops_listening_when_keyboard_interrupt_exception_occurs():
    # TODO
    pass

def test_listen_stops_listening_when_unexpected_exception_occurs():
    # TODO
    pass

def test_start_calls_listen_if_slackclient_rtm_has_valid_ok():
    # TODO
    pass

def test_start_errors_out_if_slackclient_rtm_has_invalid_ok():
    # TODO
    pass
