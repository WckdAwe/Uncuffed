import os
import uuid
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
    def store_key(key: RsaKey, friendly_name: str = None):
        if not isinstance(key, RsaKey):
            raise ValueError('First argument must be an RsaKey!')

        name = friendly_name if friendly_name else str(uuid.uuid4())
        file_name = f'{paths.PATH_WALLETS}/{name}.der'
        os.makedirs(os.path.dirname(file_name), exist_ok=True)
        with open(file_name, 'wb+') as file:
            file.write(key.exportKey(format='DER'))

    @staticmethod
    def load_key(name: str) -> RsaKey:
        with open(f'{paths.PATH_WALLETS}/{name}.der', 'rb') as file:
            key = file.read()

        return RSA.import_key(key)
