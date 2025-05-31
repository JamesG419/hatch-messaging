Hatch Messaging Service – Technical Design
==========================================

Overview
--------

Hatch Messaging Service is a unified backend for sending and receiving messages across channels (SMS, email, etc). It exposes a Django REST API for clients to send outbound messages, and also receives inbound messages via provider webhooks. All messages, contacts, and conversation history are stored in a PostgreSQL database. Outbound sends are enqueued as background tasks (using Celery) to call external providers ensuring reliability and scalability. Inbound messages from providers are handled in real time by the API and recorded in the conversation history.

Stack & Tooling
---------------

- **Django & DRF**: Python web framework and Django REST Framework for the API.
- **Celery**: Distributed task queue for asynchronous processing of sends.
- **Redis (broker)**: Message broker for Celery (Redis or RabbitMQ can be used).
- **PostgreSQL**: Relational database for persisting Contacts, Conversations, and Messages.
- **Docker Compose**: Local orchestration of services (API, DB, broker, workers) during development.

Architecture Overview
----------------------

Below is a simplified ASCII architecture diagram:

::

    +-------------------+
    |  Client / API     |
    +-------------------+
            |
            v
    +-------------------+
    | Django + DRF API  |
    +-------------------+
            |
       Save to DB
            |
            v
    +-------------------+
    |  PostgreSQL DB    |
    +-------------------+
            |
            |
        Queue Task
            |
            v
    +-------------------+
    |   Celery Worker   |
    +-------------------+
            |
    Call Provider API
            |
            v
    +-------------------+
    |  Messaging        |
    |  Providers        |
    +-------------------+

The core components are the Django REST API server, a PostgreSQL database, a Redis message broker, Celery worker processes, and external messaging providers (e.g. Twilio, Mailgun). Clients or provider webhooks communicate with the API, which persists data and enqueues tasks; Celery workers consume the Redis queues to perform background processing (such as sending messages). This asynchronous, broker-mediated design decouples the API from long-running jobs, making the system more flexible and scalable. For example, an outbound send request causes the API to create a Message record and push a Celery task; a worker later dequeues the task and calls the provider’s API to deliver the message.

Data Model Summary
------------------

- **Contact**: Represents an individual user across channels, identified by phone number or email. We resolve and unify a person’s identity across channels (e.g. the same contact on phone and email), ensuring a single Contact entry.
- **Conversation**: A thread or context of messages linked to a Contact. Conversations group related messages (e.g. a conversation per user per channel or topic). This allows tracking of multi-step exchanges.
- **Message**: Stores each message’s data (content, timestamp, status, direction, channel, provider info, etc). We use one table/model for all messages (inbound and outbound, across all channels). Each Message is associated with a Conversation and Contact. Using a single Message table simplifies querying and reporting across different directions and channels.

Inbound Flow
------------

1. **Provider webhook**: When a new message arrives at a phone number or email, the provider issues an HTTP callback to our API. For example, the phone provider sends a request to our web application via a webhook for incoming SMS. The email provider similarly posts incoming emails to a configured route.
2. **Parse and resolve**: The API endpoint extracts the incoming data (sender, recipient, body). It then finds or creates a Contact based on the sender’s identifier (phone or email).
3. **Link conversation**: The message is linked to an existing Conversation for this Contact (or a new one is created if needed), grouping it into the correct thread.
4. **Create message record**: An inbound Message record is created in the database (with direction=inbound). It stores the content and metadata and references the Contact and Conversation.
5. **Post-processing**: The service may then trigger any downstream actions (e.g. notifying a user interface, marking conversation status, etc.) and returns an appropriate HTTP response to the provider.

Outbound Flow
-------------

1. **API request**: A client (or internal system) sends an outbound message request to the REST API. The API creates a Message record (direction=outbound, status='queued') in the DB.
2. **Task queueing**: The API enqueues a Celery task to perform the send. By using a message broker (Redis), the work is done asynchronously. The main API request can return quickly without waiting for delivery.
3. **Celery worker send**: A Celery worker picks up the task from the Redis queue and calls the appropriate provider’s API (e.g. Twilio for SMS or Mailgun for email) to deliver the message.
4. **Status update**: The worker updates the Message record after sending (setting status to “sent” or “error”, and storing provider IDs). Many providers also issue delivery receipts via callbacks; these are received by our API and used to update the Message status/history as needed.

Provider Support
----------------

- **Provider abstraction**: Each provider’s logic is encapsulated in its own client/adapter implementing a common interface. This decoupling means the core service isn’t tightly coupled to one vendor. In practice we can configure a primary and backup provider per channel. Supporting multiple providers increases reliability (if one goes down, we switch to another) and makes it easy to add new channels in the future.

Design Notes
------------

- **Unified identity**: We resolve contact identity across channels (by matching phone/email) so that each real person maps to one Contact record. This ensures all their messages are correlated.
- **Single Message model**: Using one table for all messages (inbound+outbound, all channels) avoids duplication. It simplifies queries (e.g. full conversation history) and keeps our logic uniform for all directions and providers.
- **Asynchronous processing (Celery)**: We handle all external calls (sending messages) as Celery tasks, rather than in the web request path. Celery is a proven distributed task queue, and using a broker decouples producers and workers. This design makes sending reliable and scalable: the API can continue serving requests while background workers handle delivery.
