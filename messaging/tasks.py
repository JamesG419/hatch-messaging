from celery import shared_task
from .models import Message
from .providers.email import EmailProvider
from .providers.text import TextProvider

@shared_task(bind=True, max_retries=3,)
def send_message(self, message_id):
    """
    Celery task to send a message using the appropriate provider based on the message type.
    
    Args:
        self: The current task instance.
        message_id (str): The ID of the Message to be sent.
    
    Returns:
        None
    """
    try:

        message = Message.objects.get(id=message_id)
        message.status = 'SENDING'
        message.save()
        
        # Determine the provider based on the message type
        if message.message_type == 'email':
            provider = EmailProvider(
                to=message.recipient.email,
                _from=message.sender.email,
                body=message.body,
                attachments=message.attachments or []
            ) 
        elif message.message_type in ['sms', 'mms']:
            provider = TextProvider(
                to=message.recipient.phone_number,
                _from=message.sender.phone_number,
                _type=message.message_type,
                body=message.body,
                attachments=message.attachments or None
            )
        else:
            message.status = 'FAILED'
            message.last_error = "Unsupported message type"
            message.save()
            raise ValueError(message.last_error)
        
        provider.send_message()
        message.status = 'SENT'

    except Exception as exc:
        self.retry(exc=exc, countdown=60)  # Retry after 60 seconds
        message.status = 'FAILED'
        message.last_error = str(exc)
    finally:
        message.save()