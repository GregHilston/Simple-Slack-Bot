import logging
import os
import typing

import pytest
import slacksocket.errors  # type: ignore
from slack import WebClient
from slacksocket.models import SlackEvent  # type: ignore

from simple_slack_bot.simple_slack_bot import (
    SimpleSlackBot,
    SlackRequest,
)


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
    def __init__(self, injectable_bool=None, injectable_public_channels=[], injectable_private_channels=[], injectable_user_ids=[], injectable_user_names=[], injectable_channel_names=[]):
        self.injectable_bool = injectable_bool
        self.injectable_channel_names = injectable_channel_names
        self.injectable_public_channels = injectable_public_channels
        self.injectable_private_channels = injectable_private_channels
        self.injectable_user_ids = injectable_user_ids
        self.injectable_user_names = injectable_user_names

    def rtm_start(self):
        return self.injectable_bool

    def channels_list(self):
        return {"channels": [{"id": channel_id, "name": channel_name, "members": self.injectable_user_names} for channel_id, channel_name, member in zip(self.injectable_public_channels, self.injectable_channel_names, self.injectable_user_names)]}

    def groups_list(self):
        return {"groups": [{"id": value} for value in self.injectable_private_channels]}

    def users_list(self):
        return {"members": [{"id": id, "name": name} for id, name in zip(self.injectable_user_ids, self.injectable_user_names)]}


class MockListen:
    def __init__(self):
        self.was_mock_listen_called = False

    def mock_listen(self):
        self.was_mock_listen_called = True

class MockLogger:
    def addHandler(self, stream_handler):
        self.stream_handler = stream_handler

    def setLevel(self, logging_level):
        self.logging_level = logging_level

def test_peek_returns_first_and_original_iterator():
    # Given
    mock_iterator = MockIterator()
    expected_yield = (42, mock_iterator)
    mock_iterator.injectable_yield = expected_yield[0]

    # When
    actual_yield = SimpleSlackBot.peek(mock_iterator)

    # Then
    assert expected_yield[0] == actual_yield[0]
    assert expected_yield[1] == mock_iterator

def test_peek_returns_none_if_next_raises_stopiteration():
    # Given
    mock_iterator = MockIterator()
    mock_iterator.injectable_exception = StopIteration
    expected_yield = None

    # When
    actual_yield = SimpleSlackBot.peek(mock_iterator)

    # Then
    assert expected_yield == actual_yield


@pytest.mark.skip(reason="Unable to inject Class varible for mocking. Will resolve later")
def test_init_adds_streamhandler_with_debug_level_when_init_is_called_with_debug():
    # Given
    mock_logger = MockLogger()
    SimpleSlackBot.logger = mock_logger

    # When
    SimpleSlackBot(slack_bot_token="mock_slack_bot_token", debug=True)

    # Then
    assert mock_logger.stream_handler is True
    assert mock_logger.logging_level == logging.DEBUG

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
        sut._slack_bot_token == slack_bot_token
    ), "Should prioritize this value when storing over environment variable"
    assert (
        sut._slack_bot_token != os.environ["SLACK_BOT_TOKEN"]
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

    mockslack_event = SlackEvent({"type": "message"})
    mock_slackrequest = SlackRequest(python_slackclient=None, slack_event=mockslack_event)
    sut = SimpleSlackBot(slack_bot_token="Mock slack bot token")
    monitor = Monitor()
    sut._registrations = {}
    sut._registrations["message"] = [monitor.monitor_if_called]

    # When
    sut.route_request_to_callbacks(mock_slackrequest)

    # Then
    assert Monitor.was_called is True


def test_listen_stops_listening_when_slack_socket_keyboard_interrupt_exception_occurs(caplog,):
    # Given
    mock_iterator = MockIterator(injectable_exception=slacksocket.errors.ExitError)

    mock_slack_socket = MockSlackSocket()
    mock_slack_socket.mock_iterator = mock_iterator

    sut = SimpleSlackBot("mock slack bot token")
    sut._slack_socket = mock_slack_socket

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
    sut._slack_socket = mock_slack_socket

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
    sut._slack_socket = mock_slack_socket

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

    # Then


def test_listen_logs_exception_and_conntinue_when_exception_is_raised():
    pass
    # Given

    # When

    # Then


def test_helper_get_public_channel_ids_returns_public_channel_ids():
    # Given
    expected_public_channel_ids = ["1", "2", "3"]
    channel_names = ["foo", "bar", "baz"]  # needed for mock class even though unused by this test
    user_names = ["a", "b", "c"]  # needed for mock class even though unused by this test
    mock_python_slackclient = MockPythonSlackclient(injectable_public_channels=expected_public_channel_ids, injectable_channel_names=channel_names, injectable_user_names=user_names)
    sut = SimpleSlackBot()
    sut._python_slackclient = mock_python_slackclient

    # When
    actual_public_channel_ids = sut.helper_get_public_channel_ids()

    # Then
    assert expected_public_channel_ids == actual_public_channel_ids


def test_helper_get_public_channel_ids_returns_empty_list_when_found_zero_public_channel_ids():
    # Given
    expected_public_channel_ids = []
    user_names = ["a", "b", "c"]  # needed for mock class even though unused by this test
    mock_python_slackclient = MockPythonSlackclient(injectable_public_channels=expected_public_channel_ids, injectable_user_names=user_names)
    sut = SimpleSlackBot()
    sut._python_slackclient = mock_python_slackclient

    # When
    actual_public_channel_ids = sut.helper_get_public_channel_ids()

    # Then
    assert expected_public_channel_ids == actual_public_channel_ids


def test_helper_get_private_channel_ids_returns_private_channel_ids():
    # Given
    expected_private_channel_ids = ["1", "2", "3"]
    mock_python_slackclient = MockPythonSlackclient(injectable_private_channels=expected_private_channel_ids)
    sut = SimpleSlackBot()
    sut._python_slackclient = mock_python_slackclient

    # When
    actual_private_channel_ids = sut.helper_get_private_channel_ids()

    # Then
    assert expected_private_channel_ids == actual_private_channel_ids


def test_helper_get_private_channel_ids_returns_empty_list_when_found_zero_private_channel_ids():
    # Given
    expected_private_channel_ids = []
    mock_python_slackclient = MockPythonSlackclient(injectable_private_channels=expected_private_channel_ids)
    sut = SimpleSlackBot()
    sut._python_slackclient = mock_python_slackclient

    # When
    actual_private_channel_ids = sut.helper_get_private_channel_ids()

    # Then
    assert expected_private_channel_ids == actual_private_channel_ids


def test_helper_get_user_ids_returns_user_ids():
    # Given
    expected_user_ids = ["1", "2", "3"]
    user_names = ["foo", "bar", "baz"]  # needed for mock class even though unused by this test
    mock_python_slackclient = MockPythonSlackclient(injectable_user_ids=expected_user_ids, injectable_user_names=user_names)
    sut = SimpleSlackBot()
    sut._python_slackclient = mock_python_slackclient

    # When
    actual_user_ids = sut.helper_get_user_ids()

    # Then
    assert expected_user_ids == actual_user_ids


def test_helper_get_user_ids_returns_empty_list_when_found_zero_user_ids():
    # Given
    expected_user_ids = []
    mock_python_slackclient = MockPythonSlackclient(injectable_user_ids=expected_user_ids)
    sut = SimpleSlackBot()
    sut._python_slackclient = mock_python_slackclient

    # When
    actual_user_ids = sut.helper_get_user_ids()

    # Then
    assert expected_user_ids == actual_user_ids


def test_helper_get_user_names_returns_user_names():
    # Given
    user_ids = ["1", "2", "3"]  # needed for mock class even though unused by this test
    expected_user_names = ["foo", "bar", "baz"]
    mock_python_slackclient = MockPythonSlackclient(injectable_user_ids=user_ids, injectable_user_names=expected_user_names)
    sut = SimpleSlackBot()
    sut._python_slackclient = mock_python_slackclient

    # When
    actual_user_names = sut.helper_get_user_names()

    # Then
    assert expected_user_names == actual_user_names


def test_helper_get_user_names_returns_empty_list_when_found_zero_user_names():
    # Given
    user_ids = ["1", "2", "3"]  # needed for mock class even though unused by this test
    expected_user_names = []
    mock_python_slackclient = MockPythonSlackclient(injectable_user_ids=user_ids, injectable_user_names=expected_user_names)
    sut = SimpleSlackBot()
    sut._python_slackclient = mock_python_slackclient

    # When
    actual_user_names = sut.helper_get_user_names()

    # Then
    assert expected_user_names == actual_user_names

def test_helper_get_users_in_channel_returns_users():
    # Given
    channel_id = "foo"
    channel_ids = [channel_id]
    channel_names = ["foo"]
    expected_user_ids = ["1", "2", "3"]
    expected_user_names = ["a", "b", "c"]  # needed for mock class even though unused by this test

    mock_python_slackclient = MockPythonSlackclient(injectable_public_channels=channel_ids, injectable_channel_names=channel_names, injectable_user_ids=expected_user_ids, injectable_user_names=expected_user_names)

    sut = SimpleSlackBot()
    sut._python_slackclient = mock_python_slackclient

    # When
    actual_user_names = sut.helper_get_users_in_channel(channel_names[0])

    # Then
    assert expected_user_names == actual_user_names


def test_helper_get_users_in_channel_returns_empty_list_when_no_users_found():
    # Given
    channel_id = "foo"
    channel_ids = [channel_id]
    channel_names = ["foo"]
    expected_user_ids = []
    expected_user_names = []  # needed for mock class even though unused by this test

    mock_python_slackclient = MockPythonSlackclient(injectable_public_channels=channel_ids, injectable_channel_names=channel_names, injectable_user_ids=expected_user_ids, injectable_user_names=expected_user_names)

    sut = SimpleSlackBot()
    sut._python_slackclient = mock_python_slackclient

    # When
    actual_user_names = sut.helper_get_users_in_channel(channel_names[0])

    # Then
    assert expected_user_names == actual_user_names


def test_helper_user_name_to_user_id_returns_user_id_when_found():
    # Given
    expected_user_names = ["foo"]
    expected_user_ids = ["bar"]

    mock_python_slackclient = MockPythonSlackclient(injectable_user_ids=expected_user_ids, injectable_user_names=expected_user_names)

    sut = SimpleSlackBot()
    sut._python_slackclient = mock_python_slackclient

    # When
    actual_user_id = sut.helper_user_name_to_user_id(expected_user_names[0])

    # Then
    assert expected_user_ids[0] == actual_user_id


def test_helper_user_name_to_user_id_returns_none_when_nothing_is_found():
    # Given
    expected_user_names = ["foo"]
    expected_user_ids = []

    mock_python_slackclient = MockPythonSlackclient(injectable_user_ids=expected_user_ids, injectable_user_names=expected_user_names)

    sut = SimpleSlackBot()
    sut._python_slackclient = mock_python_slackclient

    # When
    actual_user_id = sut.helper_user_name_to_user_id(expected_user_names[0])

    # Then
    assert None is actual_user_id
