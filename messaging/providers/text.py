from .base import MessagingProvider


class TextProvider(MessagingProvider):
    """
    A provider for sending text messages.
    """

    def __init__(self):
        super().__init__()
        self.base_url = "https://www.provider.app/api/messages"

    def send_message(self, to, _from, type, body, attachments=None):
        """
        Send a text message using the provider's API.

        :param to: The recipient's phone number.
        :param _from: The sender's phone number.
        :param type: The type of message (e.g., 'text', 'media').
        :param body: The content of the message.
        :param attachments: Optional attachments to include in the message.
        :return: The response from the API.
        """
        data = {
            "to": to,
            "from": _from,
            "type": type,
            "body": body,
            "attachments": attachments,
            "timestamp": self.get_current_timestamp(),
        }
        return self.send_request("POST", self.base_url, data)
