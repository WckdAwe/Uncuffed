import hashlib

from abc import ABC, abstractmethod
from .JSONSerializable import JSONSerializable


class Hashable(JSONSerializable, ABC):
    @property
    def hash(self) -> str:
        return hashlib.md5(self.to_json()).hexdigest()

    @abstractmethod
    def __hash__(self):
        pass
