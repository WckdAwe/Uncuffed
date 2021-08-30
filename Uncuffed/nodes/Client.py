import operator

import Uncuffed.transactions as Transactions
import Uncuffed.messages as Messages
import Uncuffed.network as Network

from .ANode import ANode, ENodeType

from typing import List, Set, Optional
from Crypto.PublicKey.RSA import RsaKey
from Crypto.Signature import pkcs1_15
from Crypto.Signature.pkcs1_15 import PKCS115_SigScheme


class Client(ANode):

    def __init__(self, private_key: RsaKey):
        super().__init__(private_key=private_key)
        self.signer: PKCS115_SigScheme = pkcs1_15.new(self.private_key)
        self.my_UTXOs: Set[Transactions.TransactionInput] = set()   # List of unspent transactions
        self.tmp_STXOs: Set[Transactions.TransactionInput] = set()  # List of temporary spent transactions

    @property
    def node_type(self) -> int:
        return ENodeType.CLIENT

    @property
    def balance(self):
        return sum(
            filter(lambda o: o > 0, [utxo.cached_balance for utxo in self.my_UTXOs])
        )

    def send_message(self, address: str, total_gas: int, message: Messages.AMessage) -> \
            Optional[Transactions.Transaction]:
        transaction_outputs: List[Transactions.TransactionOutput] = []
        allocated_balance = 0

        if total_gas < Transactions.TransactionOutput.calculate_minimum_blabbers(message):
            return None

        t_out = Transactions.TransactionOutput(
            recipient_address=address,
            value=total_gas,
            message=message
        )

        # Allocate enough funds
        sorted_utxo: List[Transactions.TransactionInput] = sorted(self.my_UTXOs, key=operator.attrgetter('cached_balance'))
        selected_utxo: List[Transactions.TransactionInput] = []
        for utxo in sorted_utxo:
            if allocated_balance >= total_gas:
                break

            if utxo.cached_balance == -1:
                continue

            selected_utxo.append(utxo)
            allocated_balance += utxo.cached_balance

        # Verify we have enough funds
        if total_gas > allocated_balance:
            return None

        transaction_outputs.append(t_out)
        remaining_balance = allocated_balance - total_gas
        if remaining_balance > 0:
            transaction_outputs.append(
                Transactions.TransactionOutput(
                    recipient_address=self.identity,
                    value=remaining_balance,
                    message=None
                )
            )

        transaction = Transactions.Transaction(
            sender=self.identity,
            inputs=tuple(selected_utxo),
            outputs=tuple(transaction_outputs),
        )
        transaction.sign_transaction(self.signer)

        # Set UTXO as temporary 'Spent'
        for utxo in selected_utxo:
            self.my_UTXOs.remove(utxo)
            self.tmp_STXOs.add(utxo)

        self.processed_hashes.append(transaction.hash)
        Network.NetworkHandler.get_instance().broadcast_transaction(transaction=transaction)
        return transaction
