from .base import MessagingProvider


class EmailProvider(MessagingProvider):
    """
    A provider for sending emails.
    """

    def __init__(self, to, _from, body, attachments=[]):
        super().__init__()
        self.base_url = "https://www.mailplus.app/api/email"
        self.to = to
        self._from = _from
        self.body = body
        self.attachments = attachments

    def send_message(self):
        """
        Send an email using the provider's API.

        :param to: The recipient's email address.
        :param _from: The sender's email address.
        :param subject: The subject of the email.
        :param body: The content of the email.
        :param attachments: Optional attachments to include in the email.
        :return: The response from the API.
        """
        try:
            data = {
                "to": self.to,
                "from": self._from,
                "body": self.body,
                "attachments": self.attachments,
                "timestamp": self.get_current_timestamp(),
            }
            return self.send_request("POST", self.base_url, data)
        except Exception as e:
            raise Exception(f"Failed to send email: {str(e)}")
