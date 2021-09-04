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

    def get_message(self, node: Nodes.ANode):
        """
        Called only once, initially, when message is first received
        :param node:
        :return:
        """
        if self.message.message_type is Messages.EMessageType.FUND_TRANSFER or \
                self.message.message_type is Messages.EMessageType.PLAINTEXT or \
                self.message.message_type is Messages.EMessageType.PLAIN_IMAGE:
            return

        # TODO DECRYPT MESSAGE
        # if isinstance(self.message, Messages.EncryptedTextMessage):
        # pass
        # self.message.decrypt(node.private_key)
        #
        # if self.sender == node.identity:    # Decrypt my Message
        #     pass

    def __hash__(self):
        return hash((self.sender, self.inp, self.value, self.message, self.timestamp))

    def __eq__(self, other):
        return self.sender == other.sender and \
               self.value == other.value and \
               self.inp == other.inp and \
               self.timestamp == other.timestamp and \
               self.message == other.message
        # if self.inp is None or other.inp is None:
        #     if self.sender != other.sender or \
        #             self.value != other.value or \
        #             self.timestamp != other.timestamp:
        #         return False
        #
        #     if type(self.message) != type(other.message):
        #         return False
        #
        #     if self.inp is None:
        #         local_msg = self
        #         block_msg = other
        #     else:
        #         block_msg = self
        #         local_msg = other
        #
        #     if isinstance(self.message, Messages.EncryptedTextMessage):
        #         self.message.soft_encrypt( block_msg.inp)
        #
        #     return self.sender == other.sender and \
        #            self.value == other.value and \
        #            self.timestamp == other.timestamp and \
        #            self.message == other.message
        # else:
        #     return self.inp == other.inp

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
