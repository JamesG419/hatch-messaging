from django.urls import path
from messaging.views import TextInboundWebhook, EmailInboundWebhook, MessageListView, MessageDetailView, MessageDeleteView, MessageCreateView

urlpatterns = [
    path("webhook/text/inbound/", TextInboundWebhook.as_view(), name="text_inbound_webhook"),
    path("webhook/email/inbound", EmailInboundWebhook.as_view(), name="email_inbound_webhook"),
    path("messages/", MessageListView.as_view(), name="message_list"),
    path("messages/<uuid:id>/", MessageDetailView.as_view(), name="message_detail"),
    path("messages/<uuid:id>/delete/", MessageDeleteView.as_view(), name="message_delete"),
    path("messages/create/", MessageCreateView.as_view(), name="message_create"),
]