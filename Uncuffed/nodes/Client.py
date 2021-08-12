import Uncuffed.transactions as Transactions

from .ANode import ANode, ENodeType

from typing import List, Set
from Crypto.PublicKey.RSA import RsaKey
from Crypto.Signature import pkcs1_15
from Crypto.Signature.pkcs1_15 import PKCS115_SigScheme


class Client(ANode):

    def __init__(self, private_key: RsaKey):
        super().__init__(private_key=private_key)
        self.signer: PKCS115_SigScheme = pkcs1_15.new(self.private_key)
        self.my_UTXOs: Set[Transactions.TransactionInput] = set()  # List of unspent transactions

    @property
    def balance(self):
        pass    # TODO

    def send_message(self):
        pass    # TODO

