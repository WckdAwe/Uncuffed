import binascii

from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA
from Crypto.PublicKey.RSA import RsaKey

from .AMessage import EMessageType
from .PlainTextMessage import PlainTextMessage


class EncryptedTextMessage(PlainTextMessage):

    def __init__(self, message: str):
        super().__init__(message)

    def soft_encrypt(self, address: str) -> str:
        cipher_rsa = PKCS1_OAEP.new(
            RSA.import_key(binascii.unhexlify(address))
        )
        enc_session_key = cipher_rsa.encrypt(self.message.encode('utf-8'))
        return binascii.hexlify(enc_session_key).decode('ascii')

    def encrypt(self, address: str):
        self.message = self.soft_encrypt(address=address)

    def soft_decrypt(self, key: RsaKey) -> str:
        cipher_rsa = PKCS1_OAEP.new(key)
        return cipher_rsa.decrypt(binascii.unhexlify(self.message)).decode('utf-8')

    def decrypt(self, key: RsaKey):
        self.message = self.soft_decrypt(key)

    @property
    def message_type(self) -> int:
        return EMessageType.ENCRYPTED_TEXT
