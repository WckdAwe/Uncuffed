import json
import Uncuffed.messages as Messages

__M = 'Hello there...General Kenobi'
__JSON = '{"type": 1,"message": "Hello there...General Kenobi"}'
msg = Messages.PlainTextMessage(message=__M)
msg1 = Messages.PlainTextMessage(message=__M)


def test_type():
    assert msg.message_type == Messages.EMessageType.PLAINTEXT


def test_message():
    assert msg.message == __M


def test_to_json():
    s = __JSON
    assert json.loads(msg.to_json()) == json.loads(s)


def test_from_json():
    s = __JSON
    assert msg == Messages.PlainTextMessage.from_json(json.loads(s))


def test__eq():
    assert msg == msg1
