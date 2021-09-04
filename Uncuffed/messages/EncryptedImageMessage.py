import base64
import binascii
import collections

from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA
from Crypto.PublicKey.RSA import RsaKey
from werkzeug.datastructures import FileStorage

from .AMessage import EMessageType
from .ImageMessage import ImageMessage


class EncryptedImageMessage(ImageMessage):
    def __init__(self, mimetype: str, base64img: str):
        super().__init__(mimetype=mimetype, base64img=base64img)

    @property
    def message_type(self) -> int:
        return EMessageType.ENCRYPTED_IMAGE

    def soft_encrypt(self, address: str) -> str:
        from Uncuffed import rsa_long_encrypt
        enc = rsa_long_encrypt(binascii.unhexlify(address), self.message.encode('utf-8'))
        return binascii.hexlify(enc).decode('ascii')
        # cipher_rsa = PKCS1_OAEP.new(
        #     RSA.import_key(binascii.unhexlify(address))
        # )
        # enc_session_key = cipher_rsa.encrypt(self.message.encode('utf-8'))
        # return binascii.hexlify(enc_session_key).decode('ascii')

    def encrypt(self, address: str):
        self.message = self.soft_encrypt(address=address)

    def soft_decrypt(self, key: RsaKey) -> str:
        from Uncuffed import rsa_long_decrypt
        dec = rsa_long_decrypt(key, binascii.unhexlify(self.message)).decode('utf-8')

        return dec
        # cipher_rsa = PKCS1_OAEP.new(key)
        # return cipher_rsa.decrypt(binascii.unhexlify(self.message)).decode('utf-8')

    def decrypt(self, key: RsaKey):
        self.message = self.soft_decrypt(key)
