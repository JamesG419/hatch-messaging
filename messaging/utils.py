from messaging.models import Participant

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