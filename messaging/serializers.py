from rest_framework import serializers
from .models import Message, Conversation


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = [
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
        ]
        read_only_fields = ["id", "created_at"]
        extra_kwargs = {
            "conversation": {"required": True},
            "sender": {"required": True},
            "recipient": {"required": True},
            "message_type": {"required": True},
            "direction": {"required": True},
            "body": {"required": True},
            "status": {"required": True},
            "timestamp": {"required": True},
        }


class ConversationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Conversation
        fields = [
            "id",
            "participant_1",
            "participant_2",
            "last_activity",
        ]
        read_only_fields = ["id", "last_activity"]
        extra_kwargs = {
            "participant_1": {"required": True},
            "participant_2": {"required": True},
        }
