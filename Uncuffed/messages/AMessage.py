import collections

from abc import ABC, abstractmethod
from enum import Enum
from ..helpers import JSONSerializable


class EMessageType(int, Enum):
    UNDEFINED: int = 0
    TEXT: int = 1
    IMAGE: int = 2


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
        from .TextMessage import TextMessage

        classes = [TextMessage]  # TODO: Insert this inside EnumMessage
        # TODO: Exception Handling
        msg_type = int(data['type'])
        return classes[msg_type - 1].from_json(data)
