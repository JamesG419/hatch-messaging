import pytest
from unittest.mock import patch, MagicMock
from messaging.tasks import send_message


@pytest.fixture
def mock_message():
    mock = MagicMock()
    mock.id = "123"
    mock.status = "SENDING"
    mock.body = "Hello"
    mock.attachments = []
    mock.last_error = ""
    mock.save = MagicMock()
    return mock


@pytest.fixture
def mock_self():
    mock = MagicMock()
    mock.retry = MagicMock(side_effect=Exception("retry called"))
    return mock


@patch("messaging.tasks.Message")
@patch("messaging.tasks.EmailProvider")
def test_send_message_email_success(
    mock_email_provider, mock_message_model, mock_message, mock_self
):
    # Setup
    mock_message.message_type = "email"
    mock_message.recipient.email = "to@example.com"
    mock_message.sender.email = "from@example.com"
    mock_message_model.objects.get.return_value = mock_message
    provider_instance = MagicMock()
    mock_email_provider.return_value = provider_instance

    # Act
    send_message(mock_message.id)

    # Assert
    mock_message_model.objects.get.assert_called_once_with(id=mock_message.id)
    mock_email_provider.assert_called_once_with(
        to="to@example.com", _from="from@example.com", body="Hello", attachments=[]
    )
    provider_instance.send_message.assert_called_once()
    assert mock_message.status == "SENT"
    assert mock_message.save.call_count == 2  # Once before send, once after


@patch("messaging.tasks.Message")
@patch("messaging.tasks.TextProvider")
def test_send_message_sms_success(
    mock_text_provider, mock_message_model, mock_message, mock_self
):
    # Setup
    mock_message.message_type = "sms"
    mock_message.recipient.phone = "+11234567890"
    mock_message.sender.phone = "+18765432100"
    mock_message_model.objects.get.return_value = mock_message
    provider_instance = MagicMock()
    mock_text_provider.return_value = provider_instance

    # Act
    send_message(mock_message.id)

    # Assert
    mock_message_model.objects.get.assert_called_once_with(id=mock_message.id)
    mock_text_provider.assert_called_once_with(
        to="+11234567890",
        _from="+18765432100",
        _type="sms",
        body="Hello",
        attachments=None,
    )
    provider_instance.send_message.assert_called_once()
    assert mock_message.status == "SENT"
    assert mock_message.save.call_count == 2


@patch("messaging.tasks.Message")
def test_send_message_unsupported_type(mock_message_model, mock_message, mock_self):
    # Setup
    mock_message.message_type = "fax"
    mock_message_model.objects.get.return_value = mock_message

    # Act & Assert
    with pytest.raises(Exception):  # retry will raise Exception due to side_effect
        send_message(mock_message.id)
    assert mock_message.status == "FAILED"
    assert "Unsupported message type" in mock_message.last_error
    assert mock_message.save.call_count == 3


@patch("messaging.tasks.Message")
@patch("messaging.tasks.EmailProvider")
def test_send_message_provider_exception(
    mock_email_provider, mock_message_model, mock_message, mock_self
):
    # Setup
    mock_message.message_type = "email"
    mock_message.recipient.email = "to@example.com"
    mock_message.sender.email = "from@example.com"
    mock_message_model.objects.get.return_value = mock_message
    provider_instance = MagicMock()
    provider_instance.send_message.side_effect = Exception("provider failed")
    mock_email_provider.return_value = provider_instance

    # Act & Assert
    with pytest.raises(Exception):  # retry will raise Exception due to side_effect
        send_message(mock_message.id)
    print(vars(provider_instance))
    print(vars(mock_message))
    assert mock_message.status == "FAILED"
    assert "provider failed" in mock_message.last_error
    assert mock_message.save.call_count == 2

    @pytest.fixture
    def mock_message():
        mock = MagicMock()
        mock.id = "123"
        mock.status = "QUEUED"
        mock.body = "Hello"
        mock.attachments = []
        mock.last_error = ""
        mock.save = MagicMock()
        mock.recipient.email = "to@example.com"
        mock.recipient.phone = "+123456789"
        mock.sender.email = "from@example.com"
        mock.sender.phone = "+987654321"
        return mock

    @pytest.fixture
    def mock_self():
        mock = MagicMock()
        mock.retry = MagicMock(side_effect=Exception("retry called"))
        return mock

    @patch("messaging.tasks.Message")
    @patch("messaging.tasks.EmailProvider")
    def test_send_message_email_success(
        mock_email_provider, mock_message_model, mock_message
    ):
        mock_message.message_type = "email"
        mock_message_model.objects.get.return_value = mock_message
        provider_instance = MagicMock()
        mock_email_provider.return_value = provider_instance

        send_message(mock_message.id)

        mock_message_model.objects.get.assert_called_once_with(id=mock_message.id)
        mock_email_provider.assert_called_once_with(
            to="to@example.com", _from="from@example.com", body="Hello", attachments=[]
        )
        provider_instance.send_message.assert_called_once()
        assert mock_message.status == "SENT"
        assert mock_message.save.call_count == 2

    @patch("messaging.tasks.Message")
    @patch("messaging.tasks.TextProvider")
    def test_send_message_sms_success(
        mock_text_provider, mock_message_model, mock_message
    ):
        mock_message.message_type = "sms"
        mock_message.recipient.phone = "+123456789"
        mock_message.sender.phone = "+987654321"
        mock_message_model.objects.get.return_value = mock_message
        provider_instance = MagicMock()
        mock_text_provider.return_value = provider_instance

        send_message(mock_message.id)

        mock_message_model.objects.get.assert_called_once_with(id=mock_message.id)
        mock_text_provider.assert_called_once_with(
            to="+123456789",
            _from="+987654321",
            _type="sms",
            body="Hello",
            attachments=None,
        )
        provider_instance.send_message.assert_called_once()
        assert mock_message.status == "SENT"
        assert mock_message.save.call_count == 2

    @patch("messaging.tasks.Message")
    @patch("messaging.tasks.TextProvider")
    def test_send_message_mms_success(
        mock_text_provider, mock_message_model, mock_message
    ):
        mock_message.message_type = "mms"
        mock_message.recipient.phone = "+123456789"
        mock_message.sender.phone = "+987654321"
        mock_message.attachments = ["file1.jpg"]
        mock_message_model.objects.get.return_value = mock_message
        provider_instance = MagicMock()
        mock_text_provider.return_value = provider_instance

        send_message(mock_message.id)

        mock_message_model.objects.get.assert_called_once_with(id=mock_message.id)
        mock_text_provider.assert_called_once_with(
            to="+123456789",
            _from="+987654321",
            _type="mms",
            body="Hello",
            attachments=["file1.jpg"],
        )
        provider_instance.send_message.assert_called_once()
        assert mock_message.status == "SENT"
        assert mock_message.save.call_count == 2

    @patch("messaging.tasks.Message")
    def test_send_message_unsupported_type(mock_message_model, mock_message):
        mock_message.message_type = "fax"
        mock_message_model.objects.get.return_value = mock_message

        with pytest.raises(Exception):
            send_message(mock_message.id)
        assert mock_message.status == "FAILED"
        assert "Unsupported message type" in mock_message.last_error
        assert mock_message.save.call_count == 3

    @patch("messaging.tasks.Message")
    @patch("messaging.tasks.EmailProvider")
    def test_send_message_provider_exception(
        mock_email_provider, mock_message_model, mock_message
    ):
        mock_message.message_type = "email"
        mock_message.recipient.email = "to@example.com"
        mock_message.sender.email = "from@example.com"
        mock_message_model.objects.get.return_value = mock_message
        provider_instance = MagicMock()
        provider_instance.send_message.side_effect = Exception("provider failed")
        mock_email_provider.return_value = provider_instance

        with pytest.raises(Exception):
            send_message(mock_message.id)
        assert mock_message.status == "FAILED"
        assert "provider failed" in mock_message.last_error
        assert mock_message.save.call_count == 2

        @pytest.fixture
        def mock_message():
            mock = MagicMock()
            mock.id = "123"
            mock.status = "SENDING"
            mock.body = "Hello"
            mock.attachments = []
            mock.last_error = ""
            mock.save = MagicMock()
            mock.recipient.email = "to@example.com"
            mock.recipient.phone = "+123456789"
            mock.sender.email = "from@example.com"
            mock.sender.phone = "+987654321"
            return mock

        @pytest.fixture
        def mock_self():
            mock = MagicMock()
            mock.retry = MagicMock(side_effect=Exception("retry called"))
            return mock

        @patch("messaging.tasks.Message")
        @patch("messaging.tasks.EmailProvider")
        def test_send_message_email_success(
            mock_email_provider, mock_message_model, mock_message
        ):
            mock_message.message_type = "email"
            mock_message_model.objects.get.return_value = mock_message
            provider_instance = MagicMock()
            mock_email_provider.return_value = provider_instance

            send_message(mock_message.id)

            mock_message_model.objects.get.assert_called_once_with(id=mock_message.id)
            mock_email_provider.assert_called_once_with(
                to="to@example.com",
                _from="from@example.com",
                body="Hello",
                attachments=[],
            )
            provider_instance.send_message.assert_called_once()
            assert mock_message.status == "SENT"
            assert mock_message.save.call_count == 2

        @patch("messaging.tasks.Message")
        @patch("messaging.tasks.TextProvider")
        def test_send_message_sms_success(
            mock_text_provider, mock_message_model, mock_message
        ):
            mock_message.message_type = "sms"
            mock_message.recipient.phone = "+123456789"
            mock_message.sender.phone = "+987654321"
            mock_message_model.objects.get.return_value = mock_message
            provider_instance = MagicMock()
            mock_text_provider.return_value = provider_instance

            send_message(mock_message.id)

            mock_message_model.objects.get.assert_called_once_with(id=mock_message.id)
            mock_text_provider.assert_called_once_with(
                to="+123456789",
                _from="+987654321",
                _type="sms",
                body="Hello",
                attachments=None,
            )
            provider_instance.send_message.assert_called_once()
            assert mock_message.status == "SENT"
            assert mock_message.save.call_count == 2

        @patch("messaging.tasks.Message")
        @patch("messaging.tasks.TextProvider")
        def test_send_message_mms_success(
            mock_text_provider, mock_message_model, mock_message
        ):
            mock_message.message_type = "mms"
            mock_message.recipient.phone = "+123456789"
            mock_message.sender.phone = "+987654321"
            mock_message.attachments = ["file1.jpg"]
            mock_message_model.objects.get.return_value = mock_message
            provider_instance = MagicMock()
            mock_text_provider.return_value = provider_instance

            send_message(mock_message.id)

            mock_message_model.objects.get.assert_called_once_with(id=mock_message.id)
            mock_text_provider.assert_called_once_with(
                to="+123456789",
                _from="+987654321",
                _type="mms",
                body="Hello",
                attachments=["file1.jpg"],
            )
            provider_instance.send_message.assert_called_once()
            assert mock_message.status == "SENT"
            assert mock_message.save.call_count == 2

        @patch("messaging.tasks.Message")
        def test_send_message_unsupported_type(mock_message_model, mock_message):
            mock_message.message_type = "fax"
            mock_message_model.objects.get.return_value = mock_message

            with pytest.raises(Exception):
                send_message(mock_message.id)
            assert mock_message.status == "FAILED"
            assert "Unsupported message type" in mock_message.last_error
            assert mock_message.save.call_count == 3

        @patch("messaging.tasks.Message")
        @patch("messaging.tasks.EmailProvider")
        def test_send_message_provider_exception(
            mock_email_provider, mock_message_model, mock_message
        ):
            mock_message.message_type = "email"
            mock_message.recipient.email = "to@example.com"
            mock_message.sender.email = "from@example.com"
            mock_message_model.objects.get.return_value = mock_message
            provider_instance = MagicMock()
            provider_instance.send_message.side_effect = Exception("provider failed")
            mock_email_provider.return_value = provider_instance

            with pytest.raises(Exception):
                send_message(mock_message.id)
            assert mock_message.status == "FAILED"
            assert "provider failed" in mock_message.last_error
            assert mock_message.save.call_count == 2
