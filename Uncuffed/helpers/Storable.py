import json
import os
from abc import ABC, abstractmethod
from .JSONSerializable import JSONSerializable
from Uncuffed import log


class Storable(JSONSerializable, ABC):

    @staticmethod
    @abstractmethod
    def get_storage_location() -> str:
        pass

    def store_to_file(self):
        file_name = self.get_storage_location()
        os.makedirs(os.path.dirname(file_name), exist_ok=True)
        with open(file_name, 'w+') as file:
            file.write(self.to_json().decode('ascii'))

    @classmethod
    def load_from_file(cls):
        try:
            with open(cls.get_storage_location(), 'r') as file:
                json_contents = json.loads(file.read())
                return cls.from_json(json_contents)
        except Exception as e:
            log.error(e)
            return None
