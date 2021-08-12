import collections
import time
import Uncuffed.transactions as Transactions

from Crypto.Hash import SHA256
from typing import List, TYPE_CHECKING
from Uncuffed import log

from .Proofer import verify_proof
from ..helpers import Hashable

if TYPE_CHECKING:
    from Uncuffed.chain.Blockchain import Blockchain


class Block(Hashable):
    """
    Block Instance
    ------------------
    A single block instance of the blockchain. It contains:
      - Proof-of-Work and Hash of the previous block
      - List of verified transactions
      - Other block data such as Block Height and Timestamp
    """

    def __init__(self, height, proof=None, transactions=None,
                 previous_block_hash=None,
                 timestamp=None):
        self.height: int = height
        self.proof: int = proof
        self.transactions: List[Transactions.Transaction] = transactions or []
        self.previous_block_hash: str = previous_block_hash
        self.timestamp: float = timestamp or time.time()

    def is_valid(self, prev_block,
                 blockchain: 'Blockchain',
                 lite: bool = False) -> bool:
        """
        :param lite:
        :param prev_block:
        :argument blockchain: Blockchain must be provided if checking for non-lite validity.
        :return: Whether the block is valid or not
        """
        if not isinstance(prev_block, Block):
            return False
        elif self.height != prev_block.height + 1:
            log.debug(f'[BLOCK - {self.height}] Verification Failure (BLOCK ORDER)')
            return False
        elif self.previous_block_hash != prev_block.hash:
            log.debug(f'[BLOCK - {self.height}] Verification Failure (HASH)')
            return False
        elif len(self.transactions) == 0:   # TODO CHECK(and self.height != 0):
            log.debug(f'[BLOCK - {self.height}] Verification Failure (NO VERIFIED TRANSACTIONS)')
            return False
        elif self.timestamp <= prev_block.timestamp:
            log.debug(f'[BLOCK - {self.height}] Verification Failure (TIMESTAMP)')
            return False
        elif not verify_proof(prev_block.proof, self.proof):
            log.debug(f'[BLOCK - {self.height}] Verification Failure (PROOF)')
            return False
        elif not self.__verify_coinbase(lite=True):
            log.debug(f'[BLOCK - {self.height}] Verification Failure (COINBASE LITE)')
            return False
        else:
            if not lite:
                # Verify each transaction that is valid
                for indx in range(0, len(self.transactions)):
                    trans = self.transactions[indx]
                    is_coinbase = True if indx == 0 else False
                    if not trans.is_valid(blockchain=blockchain, is_coinbase=is_coinbase):
                        log.debug(f'[BLOCK - {self.height}] Verification Failure (TRANSACTION INVALID)')
                        return False

                if not self.__verify_coinbase(lite=False):
                    log.debug(f'[BLOCK - {self.height}] Verification Failure (COINBASE)')
                    return False
            return True

    def __verify_coinbase(self, lite=False):
        coinbase = self.transactions[0]
        if lite:
            return coinbase.balance_output >= self.reward
        else:
            trans_fees = [trans.cached_transaction_fee for trans in self.transactions]
            return trans_fees == coinbase.balance_output

    @property
    def hash(self) -> str:
        return SHA256.new(self.to_json()).hexdigest()

    @property
    def reward(self) -> int:
        """
        Reduce block reward by 5 per 4 mining operations.
        Total coins in circulation should be 1050
        :return:
        """
        return max([0, 50 - 5 * ((self.index + 1) // 4)])

    @classmethod
    def from_json(cls, data):
        height = int(data['height'])
        proof = int(data['proof'])
        transactions = list(map(Transactions.Transaction.from_json, data['transactions']))
        previous_block_hash = str(data['previous_hash'])
        timestamp = float(data['timestamp'])

        return cls(
            height=height,
            proof=proof,
            transactions=transactions,
            previous_block_hash=previous_block_hash,
            timestamp=timestamp
        )

    def to_dict(self) -> dict:
        return collections.OrderedDict({
            'height': self.height,
            'proof': self.proof,
            'transactions': list(map(lambda o: o.to_dict(), self.transactions)),
            'previous_hash': self.previous_block_hash,
            'timestamp': self.timestamp
        })

    def __hash__(self):
        return hash((self.proof, self.transactions, self.previous_block_hash, self.timestamp,))