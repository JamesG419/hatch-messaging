from django.urls import path
from messaging.views import TextInboundWebhook, EmailInboundWebhook, MessageListView, MessageDetailView, MessageDeleteView, MessageCreateView, ConversationListView, ConversationDetailView, ConversationDeleteView, ConversationMessagesView

urlpatterns = [
    # Inbound webhooks for text and email
    path("webhook/text/inbound/", TextInboundWebhook.as_view(), name="text_inbound_webhook"),
    path("webhook/email/inbound", EmailInboundWebhook.as_view(), name="email_inbound_webhook"),
    # Message management views
    path("messages/", MessageListView.as_view(), name="message_list"),
    path("messages/<uuid:id>/", MessageDetailView.as_view(), name="message_detail"),
    path("messages/<uuid:id>/delete/", MessageDeleteView.as_view(), name="message_delete"),
    path("messages/create/", MessageCreateView.as_view(), name="message_create"),
    # Conversation management views
    path('conversations/', ConversationListView.as_view(), name='conversation-list'),
    path('conversations/<uuid:pk>/', ConversationDetailView.as_view(), name='conversation-detail'),
    path('conversations/<uuid:pk>/delete/', ConversationDeleteView.as_view(), name='conversation-delete'),
    path('conversations/<uuid:conversation_id>/messages/', ConversationMessagesView.as_view(), name='conversation-messages'),
]