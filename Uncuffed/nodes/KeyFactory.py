import os
import uuid
from typing import Optional

import Crypto

from Crypto.PublicKey import RSA
from Crypto.PublicKey.RSA import RsaKey
from ..helpers import paths


class KeyFactory:
    @staticmethod
    def create_key() -> RsaKey:
        random = Crypto.Random.new().read
        return RSA.generate(1024, random)

    @staticmethod
    def store_key(key: RsaKey):
        if not isinstance(key, RsaKey):
            raise ValueError('First argument must be an RsaKey!')

        file_name = paths.FILE_WALLET
        os.makedirs(os.path.dirname(file_name), exist_ok=True)
        with open(file_name, 'wb+') as file:
            file.write(key.exportKey(format='DER'))

    @staticmethod
    def load_key() -> Optional[RsaKey]:
        try:
            with open(paths.FILE_WALLET, 'rb') as file:
                key = file.read()

            return RSA.import_key(key)
        except Exception:
            return None

    @staticmethod
    def load_or_generate_key() -> RsaKey:
        rsa = KeyFactory.load_key()
        if rsa:
            return rsa

        rsa = KeyFactory.create_key()
        KeyFactory.store_key(rsa)
        return rsa
