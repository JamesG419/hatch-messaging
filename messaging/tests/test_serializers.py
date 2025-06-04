import pytest
from unittest.mock import patch, MagicMock
from django.utils import timezone
from messaging.models import Message, Conversation

from messaging.serializers import (
    MessageSerializer,
    ConversationSerializer,
    MessageCreateSerializer,
)


@pytest.mark.django_db
class TestMessageSerializer:
    def test_fields_and_readonly(self):
        serializer = MessageSerializer()
        fields = set(serializer.fields.keys())
        expected_fields = {
            "id",
            "conversation",
            "sender",
            "recipient",
            "message_type",
            "direction",
            "body",
            "attachments",
            "status",
            "last_error",
            "timestamp",
            "created_at",
        }
        assert fields == expected_fields
        assert set(serializer.Meta.read_only_fields) == {"id", "created_at"}


@pytest.mark.django_db
class TestConversationSerializer:
    def test_fields_and_readonly(self):
        serializer = ConversationSerializer()
        fields = set(serializer.fields.keys())
        expected_fields = {"id", "participant_1", "participant_2", "last_activity"}
        assert fields == expected_fields
        assert set(serializer.Meta.read_only_fields) == {"id", "last_activity"}


@pytest.mark.django_db
class TestMessageCreateSerializer:
    @patch("messaging.serializers.resolve_participant")
    @patch("messaging.serializers.resolve_conversation")
    @patch("messaging.serializers.Message")
    def test_create_sms_message(
        self, mock_message, mock_resolve_conversation, mock_resolve_participant
    ):
        sender_contact = MagicMock()
        recipient_contact = MagicMock()
        mock_resolve_participant.side_effect = [sender_contact, recipient_contact]
        conversation = MagicMock()
        mock_resolve_conversation.return_value = conversation
        mock_obj = MagicMock()
        mock_message.objects.create.return_value = mock_obj

        data = {
            "sender": "+1234567890",
            "recipient": "+0987654321",
            "message_type": "sms",
            "body": "Hello",
            "attachments": [],
        }
        serializer = MessageCreateSerializer(data=data)
        assert serializer.is_valid(), serializer.errors
        message = serializer.save()

        mock_resolve_participant.assert_any_call(phone=data["sender"])
        mock_resolve_participant.assert_any_call(phone=data["recipient"])
        mock_resolve_conversation.assert_called_once_with(
            sender_contact, recipient_contact
        )
        mock_message.objects.create.assert_called_once()
        assert message == mock_obj

    @patch("messaging.serializers.resolve_participant")
    @patch("messaging.serializers.resolve_conversation")
    @patch("messaging.serializers.Message")
    def test_create_email_message(
        self, mock_message, mock_resolve_conversation, mock_resolve_participant
    ):
        sender_contact = MagicMock()
        recipient_contact = MagicMock()
        mock_resolve_participant.side_effect = [sender_contact, recipient_contact]
        conversation = MagicMock()
        mock_resolve_conversation.return_value = conversation
        mock_obj = MagicMock()
        mock_message.objects.create.return_value = mock_obj

        data = {
            "sender": "alice@example.com",
            "recipient": "bob@example.com",
            "message_type": "email",
            "body": "Hi Bob",
        }
        serializer = MessageCreateSerializer(data=data)
        assert serializer.is_valid(), serializer.errors
        message = serializer.save()

        mock_resolve_participant.assert_any_call(email=data["sender"])
        mock_resolve_participant.assert_any_call(email=data["recipient"])
        mock_resolve_conversation.assert_called_once_with(
            sender_contact, recipient_contact
        )
        mock_message.objects.create.assert_called_once()
        assert message == mock_obj

    def test_invalid_message_type(self):
        data = {
            "sender": "foo",
            "recipient": "bar",
            "message_type": "unknown",
            "body": "test",
        }
        serializer = MessageCreateSerializer(data=data)
        assert not serializer.is_valid()
        assert "message_type" in serializer.errors or serializer.errors

    def test_missing_required_fields(self):
        serializer = MessageCreateSerializer(data={})
        assert not serializer.is_valid()
        for field in ["sender", "recipient", "message_type", "body"]:
            assert field in serializer.errors
