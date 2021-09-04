import base64
import collections
from typing import AnyStr, Optional, Tuple

from werkzeug.datastructures import FileStorage

from .AMessage import EMessageType
from .PlainTextMessage import PlainTextMessage


class ImageMessage(PlainTextMessage):
    def __init__(self, mimetype: str, base64img: str):
        super().__init__(message=base64img)
        self.mimetype = mimetype

    def get_image_src(self) -> str:
        return f'data:{self.mimetype};base64, {self.message}'

    @property
    def message_type(self) -> int:
        return EMessageType.PLAIN_IMAGE

    @staticmethod
    def allowed_types() -> tuple:
        return tuple(('image/png', 'image/gif', 'image/jpeg'))

    @classmethod
    def from_file(cls, file: FileStorage):
        mimetype = file.mimetype
        if mimetype not in cls.allowed_types():
            return None

        image_string = base64.b64encode(file.stream.read()).decode('utf-8')
        return cls(mimetype, image_string)

    @classmethod
    def from_json(cls, data):
        mimetype = str(data['mimetype'])
        message = str(data['message'])

        return cls(
            mimetype=mimetype,
            base64img=message,
        )

    def to_dict(self) -> dict:
        d = collections.OrderedDict({
            'mimetype': self.mimetype,
        })
        return super().to_dict() | d

    def __eq__(self, other):
        return super().__eq__(other) and self.mimetype == other.mimetype

    def __hash__(self):
        return hash((self.message_type, self.message, self.mimetype))
