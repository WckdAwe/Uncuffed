import collections
import json
import operator
import os

import Uncuffed.transactions as Transactions
import Uncuffed.messages as Messages
import Uncuffed.network as Network
import Uncuffed.chats as Chats

from .ANode import ANode, ENodeType

from typing import List, Set, Optional
from Crypto.PublicKey.RSA import RsaKey
from Crypto.Signature import pkcs1_15
from Crypto.Signature.pkcs1_15 import PKCS115_SigScheme

from .. import log
from ..helpers.paths import FILE_NODE


class Client(ANode):

    def __init__(self, private_key: RsaKey):
        super().__init__(private_key=private_key)
        self.signer: PKCS115_SigScheme = pkcs1_15.new(self.private_key)
        self.my_UTXOs: Set[Transactions.TransactionInput] = set()
        self.my_STXOs: Set[Transactions.TransactionInput] = set()
        self.tmp_msgs: Set[Chats.MessageInstance] = set()

        self.my_UTXOs, self.my_STXOs, self.tmp_msgs, self.processed_hashes = self.load_node()

        self.refresh_balance()

    @property
    def node_type(self) -> int:
        return ENodeType.CLIENT

    @property
    def balance(self):
        return sum(
            filter(lambda o: o > 0, [(utxo.cached_balance or 0) for utxo in self.my_UTXOs])
        )

    def refresh_balance(self):
        for my_utxo in self.my_UTXOs:
            my_utxo.get_balance(blockchain=self.blockchain)

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
            self.my_STXOs.add(utxo)
        self.store_transactions()

        self.processed_hashes.append(transaction.hash)
        Network.NetworkHandler.get_instance().broadcast_transaction(transaction=transaction)

        self._add_to_chat(
            address=address,
            transaction=transaction,
            message=message,
            total_gas=total_gas
        )
        return transaction

    def _add_to_chat(self, address: str,
                     transaction: Transactions.Transaction,
                     message: Messages.AMessage,
                     total_gas: int):
        from Uncuffed.chats.Chat import Chat, get_all_chats
        from Uncuffed.chats.MessageInstance import MessageInstance
        # ---- ADD TO CHAT (DOESN'T MEAN THAT IT SHOULD  BE ACCEPTED BY ALL NODES...) ----
        chats = get_all_chats()
        chat = chats[address] if address in chats.keys() else Chat.load_from_file(
            friendly_name=address,
        )
        msg_instance = MessageInstance(
            sender=transaction.sender,
            inp=None,
            message=message,
            value=total_gas,
            timestamp=transaction.timestamp,
        )
        msg_instance.init_message()
        chat.messages.add(msg_instance)
        chat.store_to_file()
        return chat, msg_instance

    """
    THESE FILE OPS Should be extracted to a different UTXO Class
    """
    @staticmethod
    def get_storage_location() -> str:
        return FILE_NODE

    def store_transactions(self):
        file_name = self.get_storage_location()
        os.makedirs(os.path.dirname(file_name), exist_ok=True)
        with open(file_name, 'w+') as file:
            file.write(json.dumps(self.to_dict()))

    def load_node(self):
        try:
            with open(self.get_storage_location(), 'r') as file:
                json_contents = json.loads(file.read())
                my_UTXOs = set(map(Transactions.TransactionInput.from_json, json_contents['my_UTXOs']))
                my_STXOs = set(map(Transactions.TransactionInput.from_json, json_contents['my_STXOs']))
                tmp_msgs = set(map(Chats.MessageInstance.from_json, json_contents['tmp_msgs']))
                processed_hashes = list(json_contents['processed_hashes'])
                return my_UTXOs, my_STXOs, tmp_msgs, processed_hashes
        except Exception as e:
            log.error(f'Client-load_node {e}')
            self.store_transactions()
            return set(), set(), set(), list()

    def to_dict(self) -> dict:
        return collections.OrderedDict({
            'my_UTXOs': tuple(map(lambda o: o.to_dict(), self.my_UTXOs)),
            'my_STXOs': tuple(map(lambda o: o.to_dict(), self.my_STXOs)),
            'tmp_msgs': tuple(map(lambda o: o.to_dict(), self.tmp_msgs)),
            'processed_hashes': tuple(self.processed_hashes)
        })
