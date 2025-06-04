import pytest
from unittest.mock import patch, MagicMock
from messaging.providers.email import EmailProvider


@pytest.fixture
def email_provider():
    return EmailProvider()


def test_send_email_calls_send_request(email_provider):
    with patch.object(
        email_provider, "send_request", return_value={"status": "success"}
    ) as mock_send_request, patch.object(
        email_provider, "get_current_timestamp", return_value="2024-01-01T00:00:00Z"
    ):
        to = "recipient@example.com"
        _from = "sender@example.com"
        body = "Hello, this is a test email."
        attachments = ["file1.txt", "file2.jpg"]

        response = email_provider.send_message(to, _from, body, attachments)

        expected_data = {
            "to": to,
            "from": _from,
            "body": body,
            "attachments": attachments,
            "timestamp": "2024-01-01T00:00:00Z",
        }
        mock_send_request.assert_called_once_with(
            "POST", email_provider.base_url, expected_data
        )
        assert response == {"status": "success"}


def test_send_email_default_attachments(email_provider):
    with patch.object(
        email_provider, "send_request", return_value={"status": "ok"}
    ) as mock_send_request, patch.object(
        email_provider, "get_current_timestamp", return_value="2024-01-01T00:00:00Z"
    ):
        to = "recipient@example.com"
        _from = "sender@example.com"
        body = "No attachments here."

        email_provider.send_message(to, _from, body)

        called_data = mock_send_request.call_args[0][2]
        assert called_data["attachments"] == []
