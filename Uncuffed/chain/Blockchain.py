import collections

from Uncuffed import log
from typing import List

from .Block import Block
from ..helpers.Storable import Storable
from ..helpers.paths import PATH_DATA


class Blockchain(Storable):
    """
    BlockChain
    ------------------
    The BlockChain. ¯\_(ツ)_/¯
    """

    def __init__(self, blocks=None):
        self.blocks: List[Block] = blocks or []

    @staticmethod
    def get_storage_location() -> str:
        return f'{PATH_DATA}/blockchain.json'

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
    def from_json(cls, data):
        blocks = list(map(Block.from_json, data['chain']))

        return cls(
            blocks=blocks,
        )

    def to_dict(self) -> dict:
        return collections.OrderedDict({
            'length': self.size,
            'chain': tuple(map(lambda o: o.to_dict(), self.blocks)),
        })
