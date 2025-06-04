from rest_framework import serializers
from .models import Message, Conversation
from .utils import resolve_participant, resolve_conversation
from django.utils import timezone


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

class MessageCreateSerializer(serializers.Serializer):
    sender = serializers.CharField(required=True)
    recipient = serializers.CharField(required=True)
    message_type = serializers.ChoiceField(
        choices=Message.MESSAGE_TYPE_CHOICES, required=True
    )
    body = serializers.CharField(required=True)
    attachments = serializers.ListField(
        child=serializers.DictField(), required=False, allow_empty=True
    )

    def create(self, validated_data):
        if validated_data['message_type'] in ['sms', 'mms']:
            sender_contact = resolve_participant(phone=validated_data['sender'])
            recipient_contact = resolve_participant(phone=validated_data['recipient'])
        elif validated_data['message_type'] == 'email':
            sender_contact = resolve_participant(email=validated_data['sender'])
            recipient_contact = resolve_participant(email=validated_data['recipient'])
        else:
            raise serializers.ValidationError("Unsupported message type")
        

        conversation = resolve_conversation(sender_contact, recipient_contact)

        message = Message.objects.create(
            conversation=conversation,
            sender=sender_contact,
            recipient=recipient_contact,
            message_type=validated_data['message_type'],
            direction='outbound',
            body=validated_data['body'],
            attachments=validated_data.get('attachments'),
            status='QUEUED',
            timestamp=timezone.now()
        )
        return message