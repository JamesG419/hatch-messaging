from datetime import datetime

import httpx
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)


class MessagingProvider:
    """
    Base class for messaging providers.
    """

    def __init__(self, timeout=10):
        """
        Initialize the messaging provider with a timeout.

        :param timeout: The timeout for HTTP requests in seconds.
        """
        self.timeout = timeout
        self.client = httpx.Client(timeout=httpx.Timeout(timeout))

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(httpx.HTTPStatusError),
    )
    def send_request(self, method, url, data=None):
        """
        Send a message using the specified method and URL.

        :param method: The HTTP method to use (e.g., 'POST', 'GET').
        :param url: The URL to send the request to.
        :param data: The data to send in the request body (optional).
        :return: The response from the server.
        """
        response = self.client.request(method, url, json=data)
        response.raise_for_status()
        return response.json()

    def get_current_timestamp(self):
        """
        Get the current timestamp in ISO 8601 format.

        :return: The current timestamp as a string.
        """
        return datetime.now().isoformat()
