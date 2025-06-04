import pytest
from unittest.mock import patch, MagicMock
from rest_framework.test import APIRequestFactory
from rest_framework import status
from messaging.views import TextInboundWebhook
from messaging.views import EmailInboundWebhook
from messaging.views import MessageCreateView


@pytest.fixture
def api_factory():
    return APIRequestFactory()


@pytest.fixture
def valid_payload():
    return {
        "to": "+1234567890",
        "from": "+0987654321",
        "type": "text",
        "body": "Hello!",
        "messaging_provider_id": "msg-123",
        "attachments": None,
        "timestamp": "2024-06-01T12:00:00Z",
    }


@patch("messaging.views.Message")
@patch("messaging.views.resolve_participant")
@patch("messaging.views.resolve_conversation")
def test_post_success(
    mock_resolve_conversation,
    mock_resolve_participant,
    mock_message,
    api_factory,
    valid_payload,
):
    mock_message.objects.filter.return_value.exists.return_value = False
    mock_resolve_participant.side_effect = [MagicMock(), MagicMock()]
    mock_resolve_conversation.return_value = (MagicMock(), True)
    request = api_factory.post("/", valid_payload, format="json")
    view = TextInboundWebhook.as_view()
    response = view(request)
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["detail"] == "Message received successfully"
    assert mock_message.objects.create.called


@patch("messaging.views.Message")
def test_post_missing_fields(mock_message, api_factory):
    payload = {
        "to": "+1234567890",
        "from": "+1987654321",
        # missing 'type', 'body', 'messaging_provider_id'
    }
    request = api_factory.post("/", payload, format="json")
    view = TextInboundWebhook.as_view()
    response = view(request)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "error" in response.data


@patch("messaging.views.Message")
@patch("messaging.views.resolve_participant")
def test_post_duplicate_message(
    mock_resolve_participant, mock_message, api_factory, valid_payload
):
    mock_message.objects.filter.return_value.exists.return_value = True
    request = api_factory.post("/", valid_payload, format="json")
    view = TextInboundWebhook.as_view()
    response = view(request)
    assert response.status_code == status.HTTP_200_OK
    assert response.data["detail"] == "Duplicate message"


@patch("messaging.views.Message")
@patch("messaging.views.resolve_participant")
def test_post_participant_resolution_error(
    mock_resolve_participant, mock_message, api_factory, valid_payload
):
    mock_message.objects.filter.return_value.exists.return_value = False
    mock_resolve_participant.side_effect = ValueError("Invalid phone")
    request = api_factory.post("/", valid_payload, format="json")
    view = TextInboundWebhook.as_view()
    response = view(request)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "error" in response.data


@patch("messaging.views.Message")
@patch("messaging.views.resolve_participant")
@patch("messaging.views.resolve_conversation")
@patch("messaging.views.Participant")
def test_post_creates_participants_if_not_found(
    mock_participant,
    mock_resolve_conversation,
    mock_resolve_participant,
    mock_message,
    api_factory,
    valid_payload,
):
    mock_message.objects.filter.return_value.exists.return_value = False
    # First call returns None, second call returns None (simulate not found)
    mock_resolve_participant.side_effect = [None, None]
    mock_participant.objects.create.side_effect = [
        ("receiver_obj", True),
        ("sender_obj", True),
    ]
    mock_resolve_conversation.return_value = (MagicMock(), True)
    request = api_factory.post("/", valid_payload, format="json")
    view = TextInboundWebhook.as_view()
    response = view(request)
    assert response.status_code == status.HTTP_201_CREATED
    assert mock_participant.objects.create.call_count == 2


@pytest.fixture
def valid_email_payload():
    return {
        "to": "receiver@example.com",
        "from": "sender@example.com",
        "body": "Hello via email!",
        "xillio_id": "email-123",
        "attachments": None,
        "timestamp": "2024-06-01T12:00:00Z",
    }


@patch("messaging.views.Message")
@patch("messaging.views.resolve_participant")
@patch("messaging.views.resolve_conversation")
def test_email_post_success(
    mock_resolve_conversation,
    mock_resolve_participant,
    mock_message,
    api_factory,
    valid_email_payload,
):
    mock_message.objects.filter.return_value.exists.return_value = False
    mock_resolve_participant.side_effect = [MagicMock(), MagicMock()]
    mock_resolve_conversation.return_value = (MagicMock(), True)
    request = api_factory.post("/", valid_email_payload, format="json")
    view = EmailInboundWebhook.as_view()
    response = view(request)
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["detail"] == "Message received successfully"
    assert mock_message.objects.create.called


@patch("messaging.views.Message")
def test_email_post_missing_fields(mock_message, api_factory):
    payload = {
        "to": "receiver@example.com",
        "from": "sender@example.com",
        # missing 'body', 'xillio_id'
    }
    request = api_factory.post("/", payload, format="json")
    view = EmailInboundWebhook.as_view()
    response = view(request)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "error" in response.data


@patch("messaging.views.Message")
@patch("messaging.views.resolve_participant")
def test_email_post_duplicate_message(
    mock_resolve_participant, mock_message, api_factory, valid_email_payload
):
    mock_message.objects.filter.return_value.exists.return_value = True
    request = api_factory.post("/", valid_email_payload, format="json")
    view = EmailInboundWebhook.as_view()
    response = view(request)
    assert response.status_code == status.HTTP_200_OK
    assert response.data["detail"] == "Duplicate message"


@patch("messaging.views.Message")
@patch("messaging.views.resolve_participant")
def test_email_post_participant_resolution_error(
    mock_resolve_participant, mock_message, api_factory, valid_email_payload
):
    mock_message.objects.filter.return_value.exists.return_value = False
    mock_resolve_participant.side_effect = ValueError("Invalid email")
    request = api_factory.post("/", valid_email_payload, format="json")
    view = EmailInboundWebhook.as_view()
    response = view(request)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "error" in response.data


@patch("messaging.views.Message")
@patch("messaging.views.resolve_participant")
@patch("messaging.views.resolve_conversation")
@patch("messaging.views.Participant")
def test_email_post_creates_participants_if_not_found(
    mock_participant,
    mock_resolve_conversation,
    mock_resolve_participant,
    mock_message,
    api_factory,
    valid_email_payload,
):
    mock_message.objects.filter.return_value.exists.return_value = False
    mock_resolve_participant.side_effect = [None, None]
    mock_participant.objects.create.side_effect = [
        ("receiver_obj", True),
        ("sender_obj", True),
    ]
    mock_resolve_conversation.return_value = (MagicMock(), True)
    request = api_factory.post("/", valid_email_payload, format="json")
    view = EmailInboundWebhook.as_view()
    response = view(request)
    assert response.status_code == status.HTTP_201_CREATED
    assert mock_participant.objects.create.call_count == 2


@pytest.fixture
def valid_message_create_payload():
    return {
        "conversation": 1,
        "sender": 1,
        "recipient": 2,
        "message_type": "text",
        "direction": "outbound",
        "body": "Test message",
        "provider_message_id": "msg-999",
        "attachments": None,
        "status": "SENT",
        "timestamp": "2024-06-01T12:00:00Z",
    }


@patch("messaging.views.send_message")
@patch("messaging.views.MessageCreateSerializer")
def test_message_create_view_success(
    mock_serializer_cls, mock_send_message, api_factory, valid_message_create_payload
):
    mock_serializer = MagicMock()
    mock_serializer.is_valid.return_value = True
    mock_serializer.save.return_value = MagicMock(id=123)
    mock_serializer.data = valid_message_create_payload
    mock_serializer_cls.return_value = mock_serializer

    request = api_factory.post("/", valid_message_create_payload, format="json")
    view = MessageCreateView.as_view()
    response = view(request)
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data == valid_message_create_payload
    mock_serializer.is_valid.assert_called_once_with(raise_exception=True)
    mock_serializer.save.assert_called_once()
    mock_send_message.delay.assert_called_once_with(123)


@patch("messaging.views.MessageCreateSerializer")
def test_message_create_view_invalid_data(
    mock_serializer_cls, api_factory, valid_message_create_payload
):
    mock_serializer = MagicMock()
    mock_serializer.is_valid.side_effect = Exception("Invalid data")
    mock_serializer_cls.return_value = mock_serializer

    request = api_factory.post("/", valid_message_create_payload, format="json")
    view = MessageCreateView.as_view()
    with pytest.raises(Exception):
        view(request)
