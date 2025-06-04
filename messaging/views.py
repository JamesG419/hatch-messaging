from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils.dateparse import parse_datetime
from django.utils import timezone

from .utils import resolve_participant, resolve_conversation
from .models import Message, Participant

# Create your views here.


class TextInboundWebhook(APIView):
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