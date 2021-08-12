import collections
from typing import List, Optional, TYPE_CHECKING

# import Uncuffed.chain as Chain

from Uncuffed import log
from .TransactionOutput import TransactionOutput
from ..helpers import Hashable

if TYPE_CHECKING:
    from ..chain import Blockchain, Block


class TransactionInput(Hashable):
    def __init__(self, block_index: int, transaction_index: int, output_index: int):
        self.block_index: int = block_index
        self.transaction_index: int = transaction_index
        self.output_index: int = output_index

        self.__balance = None  # Helper property to calculate 'cached' balance

    @property
    def cached_balance(self) -> Optional[int]:
        return self.__balance

    def get_balance(self, blockchain: 'Blockchain') -> Optional[int]:
        try:
            output = self.find_transaction(blockchain=blockchain)
            self.__balance = output.value
            return self.__balance
        except Exception as e:
            return None

    def is_coinbase(self) -> bool:
        return self.block_index == 0 and self.transaction_index == 0 and self.output_index == 0

    def find_transaction(self, blockchain: 'Blockchain') -> Optional[TransactionOutput]:
        try:
            blocks: List['Block'] = blockchain.blocks
            block: 'Block' = blocks[self.block_index]
            transaction = block.transactions[self.transaction_index]
            return transaction.outputs[self.output_index]
        except Exception as e:
            log.error(e)
            return None

    def is_valid(self, sender: str, blockchain: 'Blockchain') -> bool:
        """
        :param blockchain:
        :param sender:
        :return:
        """
        output = self.find_transaction(blockchain=blockchain)
        if output is None:
            log.debug(f'[TRANSACTION INP - {self.hash}] Validation failed (NON-EXISTENT).')
            return False

        if output.value <= 0:
            log.debug(f'[TRANSACTION INP - {self.hash}] Validation failed (NEGATIVE VALUE).')
            return False

        self.__balance = output.value  # Cache the balance

        if output.recipient_address != sender:
            log.debug(f'[TRANSACTION INP - {self.hash}] Validation failed (BAD-SENDER).')
            return False

        # TODO
        # Check if transaction is spent
        # if check_utxos and self not in blockchain.UTXOs:
        #     log.debug(f'[TRANSACTION INP - {self.hash}] Validation failed (NOT IN UTXO LIST)')
        #     return False

        return True

    @classmethod
    def from_json(cls, data):
        block_index = int(data['block_index'])
        transaction_index = int(data['transaction_index'])
        output_index = int(data['output_index'])
        return cls(
            block_index=block_index,
            transaction_index=transaction_index,
            output_index=output_index,
        )

    def to_dict(self) -> dict:
        return collections.OrderedDict({
            'block_index': self.block_index,
            'transaction_index': self.transaction_index,
            'output_index': self.output_index,
        })

    def __hash__(self):
        return hash((self.block_index, self.transaction_index, self.block_index,))

    def __eq__(self, other):
        if not isinstance(other, TransactionInput):
            return NotImplemented

        return self.block_index == other.block_index and \
               self.transaction_index == other.transaction_index and \
               self.output_index == other.output_index
