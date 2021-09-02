import collections

from .AMessage import AMessage, EMessageType


class PlainTextMessage(AMessage):

    def __init__(self, message: str):
        self.message: str = message

    @property
    def message_type(self) -> int:
        return EMessageType.PLAINTEXT

    @classmethod
    def from_json(cls, data):
        message = str(data['message'])
        return cls(
            message=message,
        )

    def to_dict(self) -> dict:
        d = collections.OrderedDict({
            'message': self.message
        })
        return super().to_dict() | d

    def __eq__(self, other):
        return self.message == other.message

    def __hash__(self):
        return hash((self.message_type, self.message))
