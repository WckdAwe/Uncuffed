import collections
import time
import Uncuffed.transactions as Transactions

from Crypto.Hash import SHA256
from typing import List, TYPE_CHECKING, Tuple, Set, Optional
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
                 timestamp=None,
                 lite_block_hash=None):
        self.height: int = height
        self.proof: int = proof
        self.transactions: List[Transactions.Transaction] = transactions or []
        self.previous_block_hash: str = previous_block_hash
        self.timestamp: float = timestamp or time.time()

        # Merkles root simulation (For LITE ONLY)
        self.lite_block_hash: Optional[str] = None

    def clean_transactions(self):
        """
        USED ONLY FOR LITE CLIENTS.
        Clean transactions in order to save space in lite clients.
        :return:
        """
        self.lite_block_hash = self.hash
        self.transactions = []

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
        elif not lite and self.previous_block_hash != prev_block.hash:
            log.debug(f'[BLOCK - {self.height}] Verification Failure (HASH)')
            return False
        elif lite and self.previous_block_hash != prev_block.lite_block_hash:
            log.debug(f'[BLOCK - {self.height}] Verification Failure (HASH-LITE)')
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
            trans_fees = sum([trans.cached_transaction_fee for trans in self.transactions])
            coinbase_total = trans_fees + self.reward
            return coinbase_total == coinbase.balance_output

    def extract_UTXOs(self) -> set:
        """
        :return: All UTXOs generated in this block
        """
        resp = set()
        for t_indx, transaction in enumerate(self.transactions):
            outputs: Tuple[Transactions.TransactionOutput] = transaction.outputs
            for o_indx, output in enumerate(outputs):
                utxo: Transactions.TransactionInput = Transactions.TransactionInput(
                    block_index=self.height,
                    transaction_index=t_indx,
                    output_index=o_indx
                )
                resp.add(utxo)
        return resp

    def extract_STXOs(self) -> set:
        """
        :return: All spent transactions from this block
        """
        resp = set()
        for t_indx, transaction in enumerate(self.transactions):
            inputs: Tuple[Transactions.TransactionInput] = transaction.inputs
            for i_indx, inp in enumerate(inputs):
                resp.add(inp)
        return resp

    def find_UTXOs(self, address: str) -> Set[Transactions.TransactionInput]:
        """
        :param address: Receiving address
        :return: A set of all UTXOs the address received in this block
        """
        resp = set()
        for t_indx, transaction in enumerate(self.transactions):
            outputs: Tuple[Transactions.TransactionOutput] = transaction.outputs
            for o_indx, output in enumerate(outputs):
                if output.recipient_address == address:
                    utxo: Transactions.TransactionInput = Transactions.TransactionInput(
                        block_index=self.height,
                        transaction_index=t_indx,
                        output_index=o_indx
                    )
                    resp.add(utxo)
        return resp

    def find_STXOs(self, address: str) -> set:
        """
        :param address: Receiving address
        :return: A set of all STXOs the address received in this block
        """
        resp = set()
        for t_indx, transaction in enumerate(self.transactions):
            if transaction.sender != address:
                continue

            inputs: Tuple[Transactions.TransactionInput] = transaction.inputs
            for i_indx, inp in enumerate(inputs):
                resp.add(inp)
        return resp

    def update_chat(self, address: str):
        """
        :param address: Receiving address
        :return:
        """
        from Uncuffed.chats.Chat import Chat, get_all_chats
        from Uncuffed.chats.MessageInstance import MessageInstance
        chats = get_all_chats()

        for t_indx, transaction in enumerate(self.transactions):
            outputs: Tuple[Transactions.TransactionOutput] = transaction.outputs
            if transaction.sender == address:
                continue

            for o_indx, output in enumerate(outputs):
                if output.recipient_address == address:
                    utxo: Transactions.TransactionInput = Transactions.TransactionInput(
                        block_index=self.height,
                        transaction_index=t_indx,
                        output_index=o_indx
                    )
                    chat = chats[transaction.sender] if transaction.sender in chats.keys() else Chat.load_from_file(
                        friendly_name=transaction.sender,
                    )
                    msg_instance = MessageInstance(
                        sender=transaction.sender,
                        inp=utxo,
                        message=output.message,
                        value=output.value,
                        timestamp=transaction.timestamp,
                    )
                    msg_instance.init_message()
                    chat.messages.append(msg_instance)
                    chat.store_to_file()

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
        return max([0, 5000 - 5 * ((self.height + 1) // 4)])

    @classmethod
    def from_json(cls, data):
        height = int(data['height'])
        proof = int(data['proof'])
        transactions = list(map(Transactions.Transaction.from_json, data['transactions']))
        previous_block_hash = str(data['previous_hash'])
        timestamp = float(data['timestamp'])
        lite_block_hash = data['lite_block_hash'] if 'lite_block_hash' in data else None

        return cls(
            height=height,
            proof=proof,
            transactions=transactions,
            previous_block_hash=previous_block_hash,
            timestamp=timestamp,
            lite_block_hash=lite_block_hash,
        )

    def to_dict(self) -> dict:
        res = collections.OrderedDict({
            'height': self.height,
            'proof': self.proof,
            'transactions': list(map(lambda o: o.to_dict(), self.transactions)),
            'previous_hash': self.previous_block_hash,
            'timestamp': self.timestamp
        })

        if self.lite_block_hash:
            res.update({
                'lite_block_hash': self.lite_block_hash
            })

        return res

    def __hash__(self):
        return hash((self.proof, self.transactions, self.previous_block_hash, self.timestamp,))
