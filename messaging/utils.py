from messaging.models import Participant, Conversation


def resolve_participant(phone=None, email=None):
    """
    Resolve a participant by phone or email.
    If both phone and email are provided, it will return the first match found.
    If neither is provided, it raises a ValueError.
    :param phone: Phone number of the participant.
    :param email: Email address of the participant.
    :return: Participant object if found, otherwise None.
    :raises ValueError: If neither phone nor email is provided.
    """
    if phone:
        return Participant.objects.get_or_create(phone=phone)[0]
    if email:
        return Participant.objects.get_or_create(email=email)[0]
    raise ValueError("Either phone or email must be provided to resolve a participant.")


def resolve_conversation(participant_1, participant_2):
    """
    Retrieves or creates a Conversation instance between two participants, ensuring a consistent ordering of participant IDs.

    Args:
        participant_1: An object representing the first participant, expected to have an 'id' attribute.
        participant_2: An object representing the second participant, expected to have an 'id' attribute.

    Returns:
        A tuple of (Conversation instance, created), where 'created' is a boolean indicating whether a new Conversation was created.

    Raises:
        Conversation.MultipleObjectsReturned: If multiple Conversation objects are found for the given participants.
        Conversation.DoesNotExist: If no Conversation object exists and creation fails.
    """
    conversations = sorted([participant_1.id, participant_2.id])
    return Conversation.objects.get_or_create(
        participant_1_id=conversations[0], participant_2_id=conversations[1]
    )[0]
