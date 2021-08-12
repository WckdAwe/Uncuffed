import json
from abc import ABC, abstractmethod


class JSONSerializable(ABC):

    def to_json(self, **args) -> bytes:
        return json.dumps(self.to_dict(), **args).encode('utf-8')

    @classmethod
    @abstractmethod
    def from_json(cls, data):
        pass

    @abstractmethod
    def to_dict(self) -> dict:
        pass

    def __repr__(self):
        return self.to_json()

    def __str__(self):
        return str(self.to_json(indent=4).decode('utf-8'))