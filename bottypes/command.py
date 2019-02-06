from abc import ABC


class Command(ABC):
    """Defines the command interface."""

    def __init__(self): pass

    @classmethod
    def execute(cls, slack_client, args, channel_id, user, user_is_admin): pass
