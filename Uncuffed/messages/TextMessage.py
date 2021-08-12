import collections

from .AMessage import AMessage, EMessageType


class TextMessage(AMessage):

    def __init__(self, message: str):
        self.message: str = message

    @property
    def message_type(self) -> int:
        return EMessageType.TEXT

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
