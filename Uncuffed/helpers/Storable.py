import json
import os
import traceback
from abc import ABC, abstractmethod
from .JSONSerializable import JSONSerializable
from Uncuffed import log


class Storable(JSONSerializable, ABC):

    @staticmethod
    @abstractmethod
    def get_storage_location() -> str:
        pass

    def store_to_file(self, storage_location: str = None):
        file_name = storage_location or self.get_storage_location()
        os.makedirs(os.path.dirname(file_name), exist_ok=True)
        with open(file_name, 'w+') as file:
            file.write(self.to_json().decode('ascii'))

    @classmethod
    def load_from_file(cls, storage_location: str = None):
        storage_location = storage_location or cls.get_storage_location()
        try:
            with open(storage_location, 'r') as file:
                json_contents = json.loads(file.read())
                return cls.from_json(json_contents)
        except Exception as e:
            log.error(f'Storable-load_from_file {storage_location} {e}')
            return None
