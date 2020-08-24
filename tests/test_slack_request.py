import logging
import os
import typing

import pytest
import slacksocket.errors  # type: ignore
from slack import WebClient
from slacksocket.models import SlackEvent  # type: ignore

import tests.common.mocks
from simple_slack_bot.simple_slack_bot import (
    SimpleSlackBot,
    SlackRequest,
)


class MockGet:
    has_mock_get_been_called = False
    key = None

    def mock_get(self, key: str, default_value: typing.Any = None):
        self.has_mock_get_been_called = True
        self.key = key


def test_slack_request_initializer_stores_python_slackclient_and_slack_event():
    # Given
    mock_python_slack_client = 42
    mock_slack_event = 1337

    # When
    sut = SlackRequest(python_slackclient=mock_python_slack_client, slack_event=mock_slack_event)

    # Then
    assert mock_python_slack_client == sut._python_slackclient
    assert mock_slack_event == sut.slack_event


def test_get_returns_value_when_stored():
    # Given
    key = "foo"
    expected_value = "bar"
    mock_slack_event = {key: expected_value}
    sut = SlackRequest(python_slackclient=None, slack_event=mock_slack_event)

    # When
    actual_value = sut.get(key)

    # Then
    assert expected_value == actual_value


def test_get_returns_none_when_not_found():
    # Given
    mock_slack_event = {}
    sut = SlackRequest(python_slackclient=None, slack_event=mock_slack_event)

    # When
    actual_type = sut.get("foo")

    # Then
    assert None is actual_type


def test_type_calls_get_with_type_parameter():
    # Given
    mock_get = MockGet()
    sut = SlackRequest(python_slackclient=None, slack_event=None)
    sut.get = mock_get.mock_get

    # When
    sut.type

    # Then
    assert True is mock_get.has_mock_get_been_called
    assert "type" == mock_get.key


def test_subtype_calls_get_with_subtype_parameter():
    # Given
    mock_get = MockGet()
    sut = SlackRequest(python_slackclient=None, slack_event=None)
    sut.get = mock_get.mock_get

    # When
    sut.subtype

    # Then
    assert True is mock_get.has_mock_get_been_called
    assert "subtype" == mock_get.key


def test_channel_calls_get_with_channel_parameter():
    # Given
    mock_get = MockGet()
    sut = SlackRequest(python_slackclient=None, slack_event=None)
    sut.get = mock_get.mock_get

    # When
    sut.channel

    # Then
    assert True is mock_get.has_mock_get_been_called
    assert "channel" == mock_get.key


def test_thread_ts_returns_value_if_found():
    # Given
    mock_slack_event = {"thread_ts": "foo"}
    sut = SlackRequest(python_slackclient=None, slack_event=mock_slack_event)

    # When
    sut.thread_ts

    # Then
    assert "foo" == sut.thread_ts


def test_thread_ts_returns_empty_string_if_not_found():
    # Given
    mock_slack_event = {}
    sut = SlackRequest(python_slackclient=None, slack_event=mock_slack_event)

    # When
    thread_ts = sut.thread_ts

    # Then
    assert "" == thread_ts


def test_message_returns_value_if_found():
    # Given
    mock_slack_event = {"text": "foo"}
    sut = SlackRequest(python_slackclient=None, slack_event=mock_slack_event)

    # When
    message = sut.message

    # Then
    assert "foo" == message


def test_message_returns_none_if_not_found():
    # Given
    mock_slack_event = {}
    sut = SlackRequest(python_slackclient=None, slack_event=mock_slack_event)

    # When
    message = sut.message

    # Then
    assert None is message


def test_write_calls_chat_postMessage_when_channel_is_found():
    # Given
    mock_content = "foo"
    mock_channel = "bar"
    mock_slack_event = {}

    mock_python_slackclient = tests.common.mocks.MockPythonSlackclient()
    sut = SlackRequest(python_slackclient=mock_python_slackclient, slack_event=mock_slack_event)

    # When
    sut.write(mock_content, mock_channel)

    # Then
    # success


def test_write_raises_exception_if_no_channel_found():
    # Given
    mock_content = "foo"
    mock_slack_event = {}

    mock_python_slackclient = tests.common.mocks.MockPythonSlackclient()
    sut = SlackRequest(python_slackclient=mock_python_slackclient, slack_event=mock_slack_event)

    # When
    try:
        sut.write(mock_content, None)
        pytest.fail("Exception should be thrown as channel cannot be determined")
    except Exception:
        pass  # expected

    # Then
    # success


def test_write_which_raises_exception_will_reraise_exception():
    # Given
    mock_content = "foo"
    mock_channel = "bar"
    mock_slack_event = {}

    mock_python_slackclient = tests.common.mocks.MockPythonSlackclient(
        injectable_chat_postMessage_exception=Exception("mock exception")
    )
    sut = SlackRequest(python_slackclient=mock_python_slackclient, slack_event=mock_slack_event)

    # When
    sut.write(mock_content, mock_channel)

    # Then
    # success


def test_str_returns_json_representation_of_slack_event():
    class MockSlackEvent:
        def __init__(self, json):
            self.json = json

    # Given
    expected_str = "foo"
    mock_slack_event = MockSlackEvent(expected_str)
    sut = SlackRequest(python_slackclient=None, slack_event=mock_slack_event)

    # When
    actual_str = str(sut)

    # Then
    assert expected_str == actual_str
