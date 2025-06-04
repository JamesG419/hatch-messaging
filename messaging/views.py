from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics, status
from django.utils.dateparse import parse_datetime
from django.utils import timezone

from .utils import resolve_participant, resolve_conversation
from .models import Message, Participant
from .serializers import MessageSerializer, MessageCreateSerializer,ConversationSerializer
from django.shortcuts import get_object_or_404
from .tasks import send_message

# Create your views here.


class TextInboundWebhook(APIView):
    """
    API endpoint to handle inbound text message webhooks.
    POST:
        Receives and processes inbound messages from external messaging providers.
        Expects a JSON payload with the following fields:
            - to (str): The recipient's phone number.
            - from (str): The sender's phone number.
            - type (str): The type of the message (e.g., 'text').
            - body (str): The message content.
            - messaging_provider_id (str): Unique identifier for the message from the provider.
            - attachments (optional, list): Any attachments included with the message.
            - timestamp (optional, str): The time the message was sent (ISO 8601 format).
        Workflow:
            - Validates required fields.
            - Parses and defaults the timestamp if not provided.
            - Prevents duplicate messages based on provider_message_id.
            - Resolves or creates Participant objects for sender and receiver.
            - Resolves or creates a Conversation between participants.
            - Creates a Message record with the provided data.
        Responses:
            - 201 Created: Message received and processed successfully.
            - 200 OK: Duplicate message detected.
            - 400 Bad Request: Missing required fields or invalid participant data.
    """
    def post(self, request):
        data  = request.data

        reciever = data.get('to')
        sender = data.get('from')
        _type = data.get('type')
        body = data.get('body')
        message_id = data.get('messaging_provider_id')
        # Optional timestamp and attachments, may not always be provided
        attachments = data.get('attachments')
        timestamp_str = data.get('timestamp')

        if not all([reciever, sender, _type, body, message_id]):
            return Response(
                {"error": "Missing required fields"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Parse the timestamp
        # Timestamp may not always be provided, so default to current time
        timestamp = parse_datetime(timestamp_str) if timestamp_str else timezone.now()

        # Prevent duplicate messages
        if Message.objects.filter(provider_message_id=message_id).exists():
            return Response(
                {"detail": "Duplicate message"},
                status=status.HTTP_200_OK
            )
        
        # Resolve participants by phone
        try:
            reciever_participant = resolve_participant(phone=reciever)
            sender_participant = resolve_participant(phone=sender)
        except ValueError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        if not reciever_participant:
            reciever_participant = Participant.objects.create(
                phone=reciever
            )
        if not sender_participant:
            sender_participant = Participant.objects.create(
                phone=sender
            )

        # Create or get the conversation
        conversation, _ = resolve_conversation(reciever_participant, sender_participant)

        # Create the message
        Message.objects.create(
            conversation=conversation,
            sender=sender_participant,
            recipient=reciever_participant,
            message_type=_type,
            direction='inbound',
            body=body,
            provider_message_id=message_id,
            attachments=attachments,
            status='RECIEVED',
            timestamp=timestamp
        )

        return Response(
            {"detail": "Message received successfully"},
            status=status.HTTP_201_CREATED
        )
    
class EmailInboundWebhook(APIView):
    """
    APIView to handle inbound email webhooks.
    This view processes POST requests containing inbound email data, validates required fields,
    prevents duplicate messages, resolves or creates participants, associates messages with conversations,
    and stores the message in the database.
    Methods:
        post(request):
            Handles incoming POST requests with email data. Expects the following fields in the request data:
                - to (str): Recipient email address (required)
                - from (str): Sender email address (required)
                - body (str): Email message body (required)
                - xillio_id (str): Unique provider message ID (required)
                - attachments (optional): List of attachments
                - timestamp (optional): ISO-formatted timestamp string
            Returns:
                - 201 Created: If the message is successfully processed and stored.
                - 200 OK: If a duplicate message is detected.
                - 400 Bad Request: If required fields are missing or participant resolution fails.
    """
    def post(self, request):
        data  = request.data

        reciever = data.get('to')
        sender = data.get('from')
        _type = 'email'
        body = data.get('body')
        message_id = data.get('xillio_id')
        # Optional timestamp and attachments, may not always be provided
        attachments = data.get('attachments')
        timestamp_str = data.get('timestamp')

        if not all([reciever, sender, body, message_id]):
            return Response(
                {"error": "Missing required fields"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Parse the timestamp
        # Timestamp may not always be provided, so default to current time
        timestamp = parse_datetime(timestamp_str) if timestamp_str else timezone.now()

        # Prevent duplicate messages
        if Message.objects.filter(provider_message_id=message_id).exists():
            return Response(
                {"detail": "Duplicate message"},
                status=status.HTTP_200_OK
            )
        
        # Resolve participants by phone
        try:
            reciever_participant = resolve_participant(email=reciever)
            sender_participant = resolve_participant(email=sender)
        except ValueError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        if not reciever_participant:
            reciever_participant = Participant.objects.create(
                email=reciever
            )
        if not sender_participant:
            sender_participant = Participant.objects.create(
                email=sender
            )

        # Create or get the conversation
        conversation, _ = resolve_conversation(reciever_participant, sender_participant)

        # Create the message
        Message.objects.create(
            conversation=conversation,
            sender=sender_participant,
            recipient=reciever_participant,
            message_type=_type,
            direction='inbound',
            body=body,
            provider_message_id=message_id,
            attachments=attachments,
            status='RECIEVED',
            timestamp=timestamp
        )

        return Response(
            {"detail": "Message received successfully"},
            status=status.HTTP_201_CREATED
        )
    
class MessageListView(generics.ListAPIView):
    """
    APIView to list messages.
    This view retrieves all messages and returns them in a paginated format.
    """
    queryset = Message.objects.all()
    serializer_class = MessageSerializer

class MessageDetailView(generics.RetrieveAPIView):
    """
    APIView to retrieve a single message by ID.
    This view returns the details of a specific message.
    """
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    lookup_field = 'id'

class MessageDeleteView(generics.DestroyAPIView):
    """
    APIView to delete a message by ID.
    This view allows deletion of a specific message.
    """
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    lookup_field = 'id'

class MessageCreateView(generics.CreateAPIView):
    """
    APIView to create a new message.
    This view allows creation of a new message with the provided data.
    """
    
    def post(self, request):
        serializer = MessageCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        message = serializer.save()
        # Trigger the message sending task
        send_message.delay(message.id)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )
            
