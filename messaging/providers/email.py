from .base import MessagingProvider


class EmailProvider(MessagingProvider):
    """
    A provider for sending emails.
    """

    def __init__(self):
        super().__init__()
        self.base_url = "https://www.mailplus.app/api/email"

    def send_message(self, to, _from, body, attachments=[]):
        """
        Send an email using the provider's API.

        :param to: The recipient's email address.
        :param _from: The sender's email address.
        :param subject: The subject of the email.
        :param body: The content of the email.
        :param attachments: Optional attachments to include in the email.
        :return: The response from the API.
        """
        data = {
            "to": to,
            "from": _from,
            "body": body,
            "attachments": attachments,
            "timestamp": self.get_current_timestamp(),
        }
        return self.send_request("POST", self.base_url, data)
