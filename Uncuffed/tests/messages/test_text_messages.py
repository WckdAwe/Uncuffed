import json
import Uncuffed.messages as Messages

__M = 'Hello there...General Kenobi'
__JSON = '{"type": 1,"message": "Hello there...General Kenobi"}'
msg = Messages.TextMessage(message=__M)
msg1 = Messages.TextMessage(message=__M)


def test_type():
    assert msg.message_type == Messages.EMessageType.TEXT


def test_message():
    assert msg.message == __M


def test_to_json():
    s = __JSON
    assert json.loads(msg.to_json()) == json.loads(s)


def test_from_json():
    s = __JSON
    assert msg == Messages.TextMessage.from_json(json.loads(s))


def test__eq():
    assert msg == msg1
