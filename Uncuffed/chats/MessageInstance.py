import collections
from typing import Optional

from Uncuffed.helpers import JSONSerializable
import Uncuffed.messages as Messages
import Uncuffed.nodes as Nodes
import Uncuffed.transactions as Transactions


class MessageInstance(JSONSerializable):

    def __init__(self, sender: str,
                 inp: Optional[Transactions.TransactionInput],
                 message: Messages.AMessage,
                 value: int,
                 timestamp: float):
        self.sender: str = sender
        self.inp: Transactions.TransactionInput = inp
        self.value: int = value
        self.message: Messages.AMessage = Messages.AMessage() if message is None else message
        self.timestamp = timestamp

    def __hash__(self):
        return hash((self.sender, self.inp, self.value, self.message, self.timestamp))

    def __eq__(self, other):
        return self.sender == other.sender and \
               self.value == other.value and \
               self.inp == other.inp and \
               self.timestamp == other.timestamp and \
               self.message == other.message

    def __lt__(self, other):
        return self.timestamp < other.timestamp

    def __gt__(self, other):
        return self.timestamp > other.timestamp

    @classmethod
    def from_json(cls, data):
        sender = str(data['sender'])
        inp = Transactions.TransactionInput.from_json(data['inp']) if data['inp'] else None
        value = int(data['value'])
        message = Messages.AMessage.from_json(data['message'])
        timestamp = float(data['timestamp'])
        return cls(
            sender=sender,
            inp=inp,
            value=value,
            message=message,
            timestamp=timestamp,
        )

    def to_dict(self) -> dict:
        return collections.OrderedDict({
            'sender': self.sender,
            'inp': self.inp.to_dict() if self.inp else None,
            'value': self.value,
            'message': self.message.to_dict(),
            'timestamp': self.timestamp,
        })
