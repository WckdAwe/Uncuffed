from Uncuffed.helpers.Storable import Storable


class Chat(Storable):

    def __init__(self, other_address: str):
        self.other_address = other_address


    @staticmethod
    def get_storage_location() -> str:
        pass

    @classmethod
    def from_json(cls, data):
        pass

    def to_dict(self) -> dict:
        pass