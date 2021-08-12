import binascii

import Uncuffed.transactions as Transactions
import Uncuffed.chain as Chain
from .Client import Client

from typing import Dict, List
from Crypto.PublicKey.RSA import RsaKey


class Miner(Client):

    def __init__(self, private_key: RsaKey):
        super().__init__(private_key=private_key)

        # Store Verified transactions to input in block
        self.verified_transactions: Dict[str, Transactions.Transaction] = dict()

    def construct_block(self,
                        verified_transactions: List[Transactions.Transaction] = None,
                        proof=None) -> Chain.Block:

        if verified_transactions is None:
            verified_transactions = []

        last_block: Chain.Block = self.blockchain.last_block
        previous_hash = last_block.hash

        if proof is None is None:
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
                    self.identity,
                    coinbase_total
                )]
            ),
        )

        block.transactions.insert(0, coinbase)
        coinbase.sign_transaction(self.signer)

        # self.network.broadcast_block(block)  # Broadcast block to available nodes

        self.blockchain.blocks.append(block)

        # ----------------------------------
        # -- Add all Outputs as new UTXOS --
        # ----------------------------------
        # self.blockchain.UTXOs.difference_update(block.extract_STXOs())
        # self.blockchain.UTXOs = set(self.blockchain.UTXOs.union(block.extract_UTXOs()))
        #
        # # -- UPDATE MY UTXO SET --
        # my_utxos = set(block.find_UTXOs(self.identity))
        # for my_utxo in my_utxos:  # This will fail, but will cache the value
        #     my_utxo.check_validity(sender=None, blockchain=self.blockchain)
        # self.my_UTXOs = self.my_UTXOs.union(my_utxos)
        # ---------------------

        return block
