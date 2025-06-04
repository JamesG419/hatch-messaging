import pytest
from unittest.mock import patch, MagicMock
from messaging.providers.text import TextProvider


@pytest.fixture
def text_provider():
    return TextProvider()


def test_send_text_calls_send_request(text_provider):
    with patch.object(
        text_provider, "send_request", return_value={"status": "success"}
    ) as mock_send_request, patch.object(
        text_provider, "get_current_timestamp", return_value="2024-01-01T00:00:00Z"
    ):
        to = "+12345678900"
        _from = "+10987654321"
        _type = "sms"
        body = "Hello, this is a test text."
        attachments = ["file1.txt", "file2.jpg"]

        response = text_provider.send_message(to, _from, _type, body, attachments)

        expected_data = {
            "to": to,
            "from": _from,
            "type": _type,
            "body": body,
            "attachments": attachments,
            "timestamp": "2024-01-01T00:00:00Z",
        }
        mock_send_request.assert_called_once_with(
            "POST", text_provider.base_url, expected_data
        )
        assert response == {"status": "success"}


def test_send_text_default_attachments(text_provider):
    with patch.object(
        text_provider, "send_request", return_value={"status": "ok"}
    ) as mock_send_request, patch.object(
        text_provider, "get_current_timestamp", return_value="2024-01-01T00:00:00Z"
    ):
        to = "+12345678900"
        _from = "+10987654321"
        _type = "sms"
        body = "No attachments here."

        text_provider.send_message(to, _from, _type, body)

        called_data = mock_send_request.call_args[0][2]
        assert called_data["attachments"] == None
