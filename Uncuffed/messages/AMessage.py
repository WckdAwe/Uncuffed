import collections

from abc import ABC
from enum import Enum
from ..helpers import JSONSerializable


class EMessageType(int, Enum):
    FUND_TRANSFER: int = 0
    PLAINTEXT: int = 1
    ENCRYPTED_TEXT: int = 2
    PLAIN_IMAGE: int = 3
    ENCRYPTED_IMAGE: int = 4


class AMessage(JSONSerializable, ABC):

    @property
    def message_type(self) -> int:
        return EMessageType.FUND_TRANSFER

    def to_dict(self) -> dict:
        return collections.OrderedDict({
            'type': self.message_type,
        })

    @classmethod
    def from_json(cls, data):
        from .PlainTextMessage import PlainTextMessage
        from .EncryptedTextMessage import EncryptedTextMessage
        from .ImageMessage import ImageMessage
        from .EncryptedImageMessage import EncryptedImageMessage
        classes = [
            PlainTextMessage, EncryptedTextMessage,
            ImageMessage, EncryptedImageMessage
        ]  # TODO: Insert this inside EnumMessage

        # TODO: Exception Handling
        msg_type = int(data['type'])
        return classes[msg_type - 1].from_json(data)

    def __hash__(self):
        return hash((self.message_type, ))
