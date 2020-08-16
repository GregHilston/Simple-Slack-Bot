import pytest

from simple_slack_bot.simple_slack_bot import SimpleSlackBot

def test_register_actually_registers():
    # Given
    sut = SimpleSlackBot(slack_bot_token="MOCK BOT TOKEN")

    # When
    @sut.register("message")
    def mock_function():
        print("Mock function")

    # Then
    assert len(sut._registrations) == 1, "We only registered one function, therefore the count should be 1"
    assert len(sut._registrations["message"]) == 1, "We only registered one function of this type, therefore the count should be 1"
