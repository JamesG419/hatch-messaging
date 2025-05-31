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
        return Participant.objects.filter(phone=phone).first()
    if email:
        return Participant.objects.filter(email=email).first()
    if phone and email:
        return Participant.objects.filter(phone=phone, email=email).first()
    raise ValueError("Either phone or email must be provided to resolve a participant.")


def resolve_conversation(participant_1, participant_2):
    conversations = sorted([participant_1.id, participant_2.id])
    return Conversation.objects.get_or_create(
        participant_1_id=conversations[0], participant_2_id=conversations[1]
    )
