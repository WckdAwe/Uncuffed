import collections

import Uncuffed.transactions as Transactions

from Uncuffed import log
from typing import List, Set

from .Block import Block
from ..helpers.Storable import Storable
from ..helpers.paths import FILE_BLOCKCHAIN


class Blockchain(Storable):
    """
    BlockChain
    ------------------
    The BlockChain. ¯\_(ツ)_/¯
    """

    def __init__(self, blocks=None, utxos=None):
        self.blocks: List[Block] = blocks or []
        self.UTXOs: Set[Transactions.TransactionInput] = utxos or set()

    @staticmethod
    def get_storage_location() -> str:
        return FILE_BLOCKCHAIN

    @property
    def last_block(self) -> Block:
        return self.blocks[-1]

    @property
    def size(self) -> int:
        return len(self.blocks)

    def is_valid(self, lite: bool = False) -> bool:
        """
        :return: Whether the Blockchain is valid or not.
        """
        block = self.last_block
        while block.height >= 1:
            prev_block = self.blocks[block.height - 1]
            if not block.is_valid(prev_block=prev_block, blockchain=self, lite=lite):
                log.debug(f'[BLOCKCHAIN] Block height \'{block.height}\' is invalid.')
                return False
            block = prev_block

        return True

    @classmethod
    def find_block_diff(cls, old_blocks: List[Block], new_blocks: List[Block]) -> List[int]:
        if len(new_blocks) <= len(old_blocks):
            raise Exception("New chain is smaller or equal to old chain")

        diff = []
        for indx in range(0, len(old_blocks)):
            old_block = old_blocks[indx]
            new_block = new_blocks[indx]

            if old_block.hash != new_block.hash:
                diff.append(old_block.height)

        return diff

    @classmethod
    def from_json(cls, data):
        blocks = list(map(Block.from_json, data['blocks']))
        utxos = set(map(Transactions.TransactionInput.from_json, data['utxos']))
        return cls(
            blocks=blocks,
            utxos=utxos,
        )

    def to_dict(self) -> dict:
        return collections.OrderedDict({
            'length': self.size,
            'blocks': tuple(map(lambda o: o.to_dict(), self.blocks)),
            'utxos': tuple(map(lambda o: o.to_dict(), self.UTXOs)),
        })
