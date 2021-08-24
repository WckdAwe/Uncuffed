import collections

from typing import Optional
from objsize import get_deep_size
from ..helpers import Hashable
from ..messages import AMessage


class TransactionOutput(Hashable):
    def __init__(self, recipient_address: str, value: int, message: Optional[AMessage]):
        self.recipient_address: str = recipient_address
        self.value: int = value
        self.message: Optional[AMessage] = message

    def is_valid(self) -> bool:
        return self.value >= self.minimum_blabbers()

    def minimum_blabbers(self) -> int:
        return max(1, int(get_deep_size(self.message) >> 6))     # Maximum between 1 and (message size in bits) / 64

    def to_dict(self):
        return collections.OrderedDict({
            'recipient_address': self.recipient_address,
            'value': self.value,
            'message': self.message.to_dict() if self.message else None,
        })

    def __hash__(self):
        return hash((self.recipient_address, self.value, self.message))

    @classmethod
    def from_json(cls, data):
        recipient_address = str(data['recipient_address'])
        value = int(data['value'])
        message = AMessage.from_json(data['message']) if data['message'] else None
        return cls(
            recipient_address=recipient_address,
            value=value,
            message=message,
        )

    def __eq__(self, other):
        return self.recipient_address == other.recipient_address and \
               self.value == other.value and \
               self.message == other.message
