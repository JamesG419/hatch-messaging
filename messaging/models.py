from django.db import models


# Create your models here.
class Participant(models.Model):

    phone = models.CharField(max_length=20, unique=True, null=True, blank=True)
    email = models.EmailField(unique=True, null=True, blank=True)


class Conversation(models.Model):
    """Conversation model to represent a messaging conversation.
    Each conversation can have multiple messages and 2 participants.
    """

    participant_1 = models.ForeignKey(
        Participant,
        on_delete=models.CASCADE,
        related_name="participant_1_conversations",
    )
    participant_2 = models.ForeignKey(
        Participant,
        on_delete=models.CASCADE,
        related_name="participant_2_conversations",
    )
    last_activity = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("participant_1", "participant_2")


class Message(models.Model):
    """Message model to represent a message in a conversation.
    Messages must be part of a conversation, have a sender, recipient,
    message type, direction, body

    It can optionaly have attachments, a status based on where it is in the queue,
    and a last error message if it failed to send.
    The timestamp is when the message was sent or received.
    The created_at field is when the message was created in the database.
    """

    MESSAGE_TYPE_CHOICES = [
        ("SMS", "SMS"),
        ("MMS", "MMS"),
        ("EMAIL", "Email"),
    ]

    DIRECTION_CHOICES = [
        ("INCOMING", "Incoming"),
        ("OUTGOING", "Outgoing"),
    ]
    STATUS_CHOICES = [
        ("QUEUED", "Queued"),
        ("SENDING", "Sending"),
        ("SENT", "Sent"),
        ("FAILED", "Failed"),
        ("RECIEVED", "Received"),
    ]

    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE)
    sender = models.CharField(max_length=255)
    recipient = models.CharField(max_length=255)
    message_type = models.CharField(max_length=10, choices=MESSAGE_TYPE_CHOICES)
    direction = models.CharField(max_length=10, choices=DIRECTION_CHOICES)
    body = models.TextField()

    attachments = models.JSONField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    last_error = models.TextField(null=True, blank=True)

    timestamp = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
