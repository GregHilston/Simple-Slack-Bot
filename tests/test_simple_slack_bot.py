import logging
import os
import typing

import pytest
import slacksocket.errors  # type: ignore
from slack import WebClient
from slacksocket.models import SlackEvent  # type: ignore

from simple_slack_bot.simple_slack_bot import SimpleSlackBot, SlackRequest


class MockIterator:
    def __init__(self, injectable_yield=None, injectable_exception=None):
        self.injectable_yield = injectable_yield
        self.injectable_exception = injectable_exception

    def __iter__(self):
        return self

    def __next__(self):
        if self.injectable_exception:
            raise self.injectable_exception

        return self.injectable_yield


class MockSlackSocket:
    def events(self):
        return iter(self.mock_iterator)


def mock_connect():
    pass


class MockPythonSlackclient:
    def __init__(self, injectable_bool):
        self.injectable_bool = injectable_bool

    def rtm_start(self):
        return self.injectable_bool


class MockListen:
    def __init__(self):
        self.was_mock_listen_called = False

    def mock_listen(self):
        self.was_mock_listen_called = True


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


def test_listen_stops_listening_when_slack_socket_keyboard_interrupt_exception_occurs(
    caplog,
):
    # Given
    mock_iterator = MockIterator(injectable_exception=slacksocket.errors.ExitError)

    mock_slack_socket = MockSlackSocket()
    mock_slack_socket.mock_iterator = mock_iterator

    sut = SimpleSlackBot("mock slack bot token")
    sut._slackSocket = mock_slack_socket

    # When
    with caplog.at_level(logging.INFO):
        sut.listen()

    # Then
    assert SimpleSlackBot.KEYBOARD_INTERRUPT_EXCEPTION_LOG_MESSAGE in caplog.text


def test_extract_slack_socket_reponse_returns_response_when_no_exception_is_raised():
    # Given
    mock_iterator = MockIterator(injectable_yield=42)

    mock_slack_socket = MockSlackSocket()
    mock_slack_socket.mock_iterator = mock_iterator

    sut = SimpleSlackBot("mock slack bot token")
    sut._slackSocket = mock_slack_socket

    expected_first_value = 42
    expected_second_value_type = typing.Iterable

    # When
    actual_response = sut.extract_slack_socket_response()

    # Then
    assert expected_first_value == actual_response[0]
    assert isinstance(actual_response[1], expected_second_value_type)


@pytest.mark.parametrize(
    "slacksocket_error",
    [
        slacksocket.errors.APIError,
        slacksocket.errors.ConfigError,
        slacksocket.errors.APINameError,
        slacksocket.errors.ConnectionError,
        slacksocket.errors.TimeoutError,
    ],
)
def test_extract_slack_socket_reponse_returns_none_when_non_exiterror_slack_socket_exception_occurs(
    slacksocket_error,
):
    # Given
    mock_iterator = MockIterator(injectable_exception=slacksocket_error)

    mock_slack_socket = MockSlackSocket()
    mock_slack_socket.mock_iterator = mock_iterator

    sut = SimpleSlackBot("mock slack bot token")
    sut._slackSocket = mock_slack_socket

    expected_response = None

    # When
    actual_response = sut.extract_slack_socket_response()

    # Then
    assert expected_response == actual_response


def test_start_calls_listen_if_slackclient_rtm_has_valid_ok():
    # Given
    sut = SimpleSlackBot("mock slack bot token")

    sut.connect = mock_connect

    mock_python_slackclient = MockPythonSlackclient(True)
    sut._python_slackclient = mock_python_slackclient

    mock_listen = MockListen()
    sut.listen = mock_listen.mock_listen

    # When
    sut.start()

    # Then
    assert mock_listen.was_mock_listen_called is True


def test_start_errors_out_if_slackclient_rtm_has_invalid_ok():
    # Given
    sut = SimpleSlackBot("mock slack bot token")

    sut.connect = mock_connect

    mock_python_slackclient = MockPythonSlackclient(False)
    sut._python_slackclient = mock_python_slackclient

    mock_listen = MockListen()
    sut.listen = mock_listen.mock_listen

    # When
    sut.start()

    # Then
    assert mock_listen.was_mock_listen_called is False


def test_listen_calls_route_request_to_callbacks_when_valid_request():
    pass
    # Given

    # When
    # sut.listen()

    # Then
