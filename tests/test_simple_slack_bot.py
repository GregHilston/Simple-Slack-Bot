import os

import pytest

from simple_slack_bot.simple_slack_bot import SimpleSlackBot


def test_init_prefers_paramters_over_environment_variables():
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
