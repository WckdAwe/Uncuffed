import collections

from abc import ABC, abstractmethod
from enum import Enum
from ..helpers import JSONSerializable


class EMessageType(int, Enum):
    UNDEFINED: int = 0
    PLAINTEXT: int = 1
    ENCRYPTED_TEXT: int = 2
    PLAIN_IMAGE: int = 3


class AMessage(JSONSerializable, ABC):

    @property
    def message_type(self) -> int:
        return EMessageType.UNDEFINED

    @abstractmethod
    def to_dict(self) -> dict:
        return collections.OrderedDict({
            'type': self.message_type,
        })

    @classmethod
    @abstractmethod
    def from_json(cls, data):
        from .PlainTextMessage import TextMessage

        classes = [TextMessage]  # TODO: Insert this inside EnumMessage
        # TODO: Exception Handling
        msg_type = int(data['type'])
        return classes[msg_type - 1].from_json(data)
