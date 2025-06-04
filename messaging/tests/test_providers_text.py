import pytest
from unittest.mock import patch, MagicMock
from messaging.providers.text import TextProvider

@pytest.fixture
def text_provider():
    return TextProvider(
        to="+12345678900",
        _from="+09876543210",
        _type="text",
        body="Hello, world!",
        attachments=["file1.jpg", "file2.pdf"]
    )

def test_text_provider_initialization(text_provider):
    assert text_provider.to == "+12345678900"
    assert text_provider._from == "+09876543210"
    assert text_provider.type == "text"
    assert text_provider.body == "Hello, world!"
    assert text_provider.attachments == ["file1.jpg", "file2.pdf"]
    assert text_provider.base_url == "https://www.provider.app/api/messages"

@patch.object(TextProvider, "send_request")
@patch.object(TextProvider, "get_current_timestamp", return_value="2024-01-01T00:00:00Z")
def test_send_message_calls_send_request(mock_timestamp, mock_send_request, text_provider):
    # Patch the attribute name if needed
    # The code uses self._attachments, but __init__ sets self.attachments
    # So, set _attachments for the test
    text_provider._attachments = text_provider.attachments

    mock_send_request.return_value = {"status": "success"}
    response = text_provider.send_message()
    expected_data = {
        "to": "+12345678900",
        "from": "+09876543210",
        "type": "text",
        "body": "Hello, world!",
        "attachments": ["file1.jpg", "file2.pdf"],
        "timestamp": "2024-01-01T00:00:00Z",
    }
    mock_send_request.assert_called_once_with("POST", text_provider.base_url, expected_data)
    assert response == {"status": "success"}

@patch.object(TextProvider, "send_request")
@patch.object(TextProvider, "get_current_timestamp", return_value="2024-01-01T00:00:00Z")
def test_send_message_without_attachments(mock_timestamp, mock_send_request):
    provider = TextProvider(
        to="+11111111111",
        _from="+22222222222",
        _type="text",
        body="No attachments"
    )
    # Patch _attachments to None for test consistency
    provider._attachments = None

    mock_send_request.return_value = {"status": "ok"}
    response = provider.send_message()
    expected_data = {
        "to": "+11111111111",
        "from": "+22222222222",
        "type": "text",
        "body": "No attachments",
        "attachments": None,
        "timestamp": "2024-01-01T00:00:00Z",
    }
    mock_send_request.assert_called_once_with("POST", provider.base_url, expected_data)
    assert response == {"status": "ok"}