import pytest
from unittest.mock import patch, MagicMock
from messaging.providers.base import MessagingProvider
import httpx
import tenacity


def test_init_sets_timeout_and_client():
    provider = MessagingProvider(timeout=5)
    assert provider.timeout == 5
    assert isinstance(provider.client, httpx.Client)
    assert provider.client.timeout.connect == 5


@patch("httpx.Client.request")
def test_send_request_success(mock_request):
    provider = MessagingProvider()
    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {"result": "ok"}
    mock_request.return_value = mock_response

    result = provider.send_request("POST", "http://test.com", data={"foo": "bar"})
    mock_request.assert_called_once_with("POST", "http://test.com", json={"foo": "bar"})
    assert result == {"result": "ok"}


@patch("httpx.Client.request")
def test_send_request_raises_for_status_error(mock_request):
    provider = MessagingProvider()
    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        "error", request=MagicMock(), response=MagicMock()
    )
    mock_request.return_value = mock_response
    print("mock_response:", mock_response)
    print("mock_request:", mock_request)
    with pytest.raises(tenacity.RetryError):
        provider.send_request("GET", "http://fail.com")


def test_get_current_timestamp_format():
    provider = MessagingProvider()
    ts = provider.get_current_timestamp()
    # ISO 8601 format: 'YYYY-MM-DDTHH:MM:SS'
    assert "T" in ts
    assert len(ts) >= 19
