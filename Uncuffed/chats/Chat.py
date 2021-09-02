import collections
import os
import uuid

from typing import List, Dict, Set

from Uncuffed import log
from Uncuffed.helpers.Storable import Storable
from Uncuffed.helpers.paths import PATH_CHATS

from .MessageInstance import MessageInstance


class Chat(Storable):

    def __init__(self, other_address: str, messages: Set[MessageInstance], friendly_name: str = None):
        self.other_address = other_address
        self.messages: Set[MessageInstance] = messages

        if not friendly_name:
            self.friendly_name = str(uuid.uuid4())
        else:
            self.friendly_name = friendly_name

    @staticmethod
    def get_storage_location() -> str:
        return PATH_CHATS

    @property
    def local_storage_location(self) -> str:
        return f'{Chat.get_storage_location()}/{self.friendly_name}.json'

    def store_to_file(self, storage_location: str = None):
        return super().store_to_file(
            storage_location=(storage_location or self.local_storage_location)
        )

    @classmethod
    def load_from_file(cls, friendly_name: str = None):
        if friendly_name is None:
            raise ValueError('A friendly name must be declared')

        storage_location = f'{cls.get_storage_location()}/{friendly_name}.json'

        class_ = super().load_from_file(
            storage_location=storage_location
        )

        # Create New class
        if not class_:
            address = friendly_name
            log.info(f'Creating chat log for {friendly_name}')
            class_ = cls(
                other_address=address,
                messages=set(),
            )
            class_.store_to_file()

        return class_

    @classmethod
    def from_json(cls, data):
        other_address = str(data['other_address'])
        friendly_name = str(data['friendly_name'])
        messages = set(map(MessageInstance.from_json, data['messages']))
        return cls(
            other_address=other_address,
            friendly_name=friendly_name,
            messages=messages,
        )

    def to_dict(self) -> dict:
        return collections.OrderedDict({
            'other_address': self.other_address,
            'friendly_name': self.friendly_name,
            'messages': tuple(map(lambda o: o.to_dict(), self.messages)),
        })


# TODO: There should be a chat manager... but then again...
# it's just an exercise.
def get_all_chats() -> Dict[str, Chat]:
    chats = {}
    for filename in os.listdir(Chat.get_storage_location()):
        name, file_extension = os.path.splitext(filename)
        chat = Chat.load_from_file(friendly_name=name)
        chats[chat.other_address] = chat
    return chats
