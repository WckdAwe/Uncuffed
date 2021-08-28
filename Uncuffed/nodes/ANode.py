import binascii
import collections

from abc import ABC, abstractmethod
from enum import Enum
from typing import List

from Crypto.PublicKey.RSA import RsaKey

from Uncuffed.chain.Blockchain import Blockchain


class ENodeType(int, Enum):
    UNDEFINED: int = 0
    MINER: int = 1
    CLIENT: int = 2


class ANode(ABC):

    def __init__(self, private_key: RsaKey):
        self.blockchain = Blockchain.load_from_file() or Blockchain()
        self.private_key: RsaKey = private_key
        self.public_key: RsaKey = self.private_key.publickey()
        self.processed_hashes: List[str] = []

    @property
    def node_type(self) -> int:
        return ENodeType.UNDEFINED

    @property
    def identity(self) -> str:
        """
        ASCII Representation of node's public_key
        :return:
        """
        return binascii.hexlify(self.public_key.exportKey(format='DER')).decode('ascii')

    def __str__(self):
        return self.identity
