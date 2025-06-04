import pytest
from unittest.mock import patch, MagicMock
from messaging.providers.email import EmailProvider

@pytest.fixture
def email_provider():
    return EmailProvider(
        to="recipient@example.com",
        _from="sender@example.com",
        body="Hello, this is a test email.",
        attachments=["file1.txt", "file2.pdf"]
    )

def test_email_provider_initialization(email_provider):
    assert email_provider.to == "recipient@example.com"
    assert email_provider._from == "sender@example.com"
    assert email_provider.body == "Hello, this is a test email."
    assert email_provider.attachments == ["file1.txt", "file2.pdf"]
    assert email_provider.base_url == "https://www.mailplus.app/api/email"

@patch.object(EmailProvider, "send_request")
@patch.object(EmailProvider, "get_current_timestamp", return_value="2024-01-01T00:00:00Z")
def test_send_message_calls_send_request(mock_timestamp, mock_send_request, email_provider):
    mock_send_request.return_value = {"status": "success"}
    response = email_provider.send_message()
    expected_data = {
        "to": "recipient@example.com",
        "from": "sender@example.com",
        "body": "Hello, this is a test email.",
        "attachments": ["file1.txt", "file2.pdf"],
        "timestamp": "2024-01-01T00:00:00Z",
    }
    mock_send_request.assert_called_once_with("POST", email_provider.base_url, expected_data)
    assert response == {"status": "success"}

def test_email_provider_default_attachments():
    provider = EmailProvider("to@x.com", "from@x.com", "body")
    assert provider.attachments == []