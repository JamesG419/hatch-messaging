from django.urls import path
from messaging.views import TextInboundWebhook, EmailInboundWebhook

urlpatterns = [
    path("webhook/text/inbound/", TextInboundWebhook.as_view(), name="text_inbound_webhook"),
    path("webhook/email/inbound", EmailInboundWebhook.as_view(), name="email_inbound_webhook"),
]