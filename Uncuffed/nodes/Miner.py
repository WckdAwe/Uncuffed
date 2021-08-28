import threading

import Uncuffed.transactions as Transactions
import Uncuffed.chain as Chain
from . import ENodeType

from .Client import Client

from Uncuffed import log
from typing import Dict, List, Optional
from Crypto.PublicKey.RSA import RsaKey


class Miner(Client):

    def __init__(self, private_key: RsaKey):
        super().__init__(private_key=private_key)

        # Store Verified transactions to input in the next block
        self.verified_transactions: Dict[str, Transactions.Transaction] = dict()

        # Settings
        self.__is_mining: bool = False
        self.__mining_thread = threading.Thread(target=self.__mine, daemon=True)

        # Construct Genesis Block on empty Blockchain
        if self.blockchain.size == 0:
            self._construct_genesis_block()

    @property
    def node_type(self) -> int:
        return ENodeType.MINER

    def _construct_genesis_block(self):
        self.construct_block(
            proof=42,
            previous_hash="Samira-mira-mira-e-e-Waka-Waka-e-e"
        )

    def construct_block(self,
                        verified_transactions: List[Transactions.Transaction] = None,
                        proof=None,
                        previous_hash=None) -> Chain.Block:

        if verified_transactions is None:
            verified_transactions = []

        if proof is None and previous_hash is None:
            last_block: Chain.Block = self.blockchain.last_block
            previous_hash = last_block.hash
            proof = Chain.proof_of_work(last_block.proof)

        block = Chain.Block(
            height=len(self.blockchain.blocks),
            proof=proof,
            transactions=verified_transactions,
            previous_block_hash=previous_hash)

        coinbase_total = block.reward + sum([trans.cached_transaction_fee for trans in verified_transactions])

        # Coinbase Transaction
        coinbase = Transactions.Transaction(
            sender=self.identity,
            outputs=tuple([
                Transactions.TransactionOutput(
                    recipient_address=self.identity,
                    value=coinbase_total,
                    message=None,
                )]
            ),
        )
        coinbase.sign_transaction(self.signer)
        block.transactions.insert(0, coinbase)

        # self.network.broadcast_block(block)  # TODO: Broadcast block to available nodes

        self.blockchain.blocks.append(block)

        # ----------------------------------
        # -- Add all Outputs as new UTXOS --
        # ----------------------------------
        self.blockchain.UTXOs.difference_update(block.extract_STXOs())
        self.blockchain.UTXOs = set(self.blockchain.UTXOs.union(block.extract_UTXOs()))

        # -- UPDATE MY UTXO SET --
        my_utxos = set(block.find_UTXOs(self.identity))
        for my_utxo in my_utxos:  # This will fail, but will cache the value
            my_utxo.is_valid(sender=None, blockchain=self.blockchain)
        self.my_UTXOs = self.my_UTXOs.union(my_utxos)
        # ---------------------

        return block

    @property
    def is_mining(self):
        return self.__is_mining

    def toggle_mining(self, mine: bool = None):
        self.__is_mining = not self.__is_mining if mine is None else mine

        if self.__is_mining:
            log.info('Started mining...')
            self.__mining_thread.start()
        else:
            log.info('Stopped mining...')
            self.__mining_thread = threading.Thread(target=self.__mine, daemon=True)

    def __mine(self):
        while self.__is_mining:
            self.manual_mine()

    def manual_mine(self) -> Optional[Chain.Block]:
        """
        Mine --WITHOUT TRANSACTION LIMIT--
        :return:
        """
        if not self.verified_transactions:
            return None

        transactions: Dict[str, Transactions.Transaction] = self.verified_transactions
        self.verified_transactions = dict()
        new_block = self.construct_block(
            verified_transactions=list(transactions.values()),
        )
        return new_block

    def add_transaction(self, transaction: Transactions.Transaction) -> bool:
        if not isinstance(transaction, Transactions.Transaction):
            raise ValueError('Transaction is not a valid Transaction object!')

        t_hash = transaction.hash
        if t_hash in self.verified_transactions.keys():
            log.debug(f'[TRANSACTION - {t_hash}] Addition to list rejected (Already verified)')
            return False

        if not transaction.is_valid(blockchain=self.blockchain):  # TODO: , check_utxos=True):
            return False

        self.verified_transactions[t_hash] = transaction
        return True
