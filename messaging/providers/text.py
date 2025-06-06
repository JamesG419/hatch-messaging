from .base import MessagingProvider


class TextProvider(MessagingProvider):
    """
    A provider for sending text messages.
    """

    def __init__(self, to, _from, _type, body, attachments=None):
        super().__init__()
        self.base_url = "https://www.provider.app/api/messages"
        self.to = to
        self._from = _from
        self.type = _type
        self.body = body
        self.attachments = attachments

    def send_message(self):
        """
        Send a text message using the provider's API.

        :param to: The recipient's phone number.
        :param _from: The sender's phone number.
        :param type: The type of message (e.g., 'text', 'media').
        :param body: The content of the message.
        :param attachments: Optional attachments to include in the message.
        :return: The response from the API.
        """
        try:
            data = {
                "to": self.to,
                "from": self._from,
                "type": self.type,
                "body": self.body,
                "attachments": self.attachments,
                "timestamp": self.get_current_timestamp(),
            }
            return self.send_request("POST", self.base_url, data)
        except Exception as e:
            raise Exception(f"Failed to send text message: {str(e)}")
