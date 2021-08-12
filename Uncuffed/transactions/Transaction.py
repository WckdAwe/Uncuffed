import binascii
import collections
import time

from typing import Tuple, TYPE_CHECKING
from Uncuffed import log
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from Crypto.Signature.pkcs1_15 import PKCS115_SigScheme

from .TransactionInput import TransactionInput
from .TransactionOutput import TransactionOutput
from ..helpers import Hashable

if TYPE_CHECKING:
    from ..chain import Blockchain


class Transaction(Hashable):

    def __init__(self,
                 sender: str,
                 inputs: Tuple[TransactionInput],
                 outputs: Tuple[TransactionOutput],
                 signature: str = None,
                 timestamp: float = None):
        self.sender = sender
        self.inputs: Tuple[TransactionInput] = inputs
        self.outputs: Tuple[TransactionOutput] = outputs
        self.timestamp: float = timestamp or time.time()
        self.signature: str = signature

        # Helper variables to avoid unnecessary calculations
        self.__balance_input: int = -1
        self.__transaction_fee: int = -1

    @property
    def cached_balance_input(self) -> int:
        return self.__balance_input

    @property
    def cached_transaction_fee(self) -> int:
        return self.__transaction_fee

    @property
    def balance_output(self) -> int:
        return sum([out.value for out in self.outputs])

    def __calculate_balance_input(self) -> int:
        self.__balance_input = sum([inp.cached_balance for inp in self.inputs])
        return self.__balance_input

    def __calculate_transaction_fee(self, coinbase=False) -> int:
        self.__transaction_fee = 0 if coinbase else self.__calculate_balance_input() - self.balance_output
        return self.__transaction_fee

    def sign_transaction(self, signer: PKCS115_SigScheme):
        self.signature = None
        h = SHA256.new(self.to_json())
        self.signature = binascii.hexlify(signer.sign(h)).decode('ascii')

    def verify_signature(self) -> bool:
        """
        :return: Whether the signature belongs to the actual sender or not
        """
        signature = self.signature
        result = False
        try:
            self.signature = None  # Remove signature to verify hash

            der_key = binascii.unhexlify(self.sender)

            sig = binascii.unhexlify(signature)

            public_key = RSA.import_key(der_key)
            h = SHA256.new(self.to_json())

            signer = pkcs1_15.new(public_key)
            signer.verify(h, sig)  # Verify that the hash and transaction match
            result = True
        except (ValueError, TypeError, Exception) as e:
            result = False
            log.error(e)
        finally:
            self.signature = signature  # Reset signature
            return result

    def is_valid(self, blockchain: 'Blockchain', is_coinbase=False) -> bool:
        if not self.verify_signature():
            log.debug(f'[TRANSACTION - {self.hash}] Validation failed (SIGNATURE)')
            return False

        for inp in self.inputs:
            if not inp.is_valid(
                    sender=self.sender,
                    blockchain=blockchain,
                    # check_utxos=check_utxos # TODO
            ):
                log.debug(f'[TRANSACTION - {self.hash}] Validation failed (INPUTS)')
                return False

        for out in self.outputs:
            if not out.is_valid():
                log.debug(f'[TRANSACTION - {self.hash}] Validation failed (OUTPUTS)')
                return False

        if not self.__calculate_transaction_fee(coinbase=is_coinbase) >= 0:  # Output is more than available input
            log.debug(f'[TRANSACTION - {self.hash}] Validation failed (TRANSACTION FEE - NEGATIVE)')
            return False

        return True  # TODO: Check previous blocks!

    def __hash__(self):
        return hash((self.sender, self.inputs, self.outputs, self.timestamp, self.signature))

    @classmethod
    def from_json(cls, data):
        sender = str(data['sender'])
        inputs = tuple(map(TransactionInput.from_json, data['inputs']))
        outputs = tuple(map(TransactionOutput.from_json, data['outputs']))
        timestamp = float(data['timestamp'])
        signature = str(data['signature'])
        return cls(
            sender=sender,
            inputs=inputs,
            outputs=outputs,
            timestamp=timestamp,
            signature=signature
        )

    def to_dict(self) -> dict:
        return collections.OrderedDict({
            'sender': self.sender,
            'inputs': tuple(map(lambda o: o.to_dict(), self.inputs)),
            'outputs': tuple(map(lambda o: o.to_dict(), self.outputs)),
            'timestamp': self.timestamp,
            'signature': self.signature,
        })
