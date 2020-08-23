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


def test_slack_request_initializer_stores_python_slackclient_and_slack_event():
    # Given
    mock_python_slack_client = 42
    mock_slack_event = 1337

    # When
    sut = SlackRequest(python_slackclient=mock_python_slack_client, slack_event=mock_slack_event)

    # Then
    assert mock_python_slack_client == sut._python_slackclient
    assert mock_slack_event == sut.slack_event
