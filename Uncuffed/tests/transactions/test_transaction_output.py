import Uncuffed.transactions as Transactions

from Uncuffed.tests.messages.test_text_messages import msg as __MSG, __JSON as __MSG_JSON

__RECIPIENT = 'DemoUser'
__VALUE = 42
__T_OUT = Transactions.TransactionOutput(
    recipient_address=__RECIPIENT,
    value=__VALUE,
    message=__MSG
)

# __JSON = ''.join(('{"recipient_address": "', __RECIPIENT,
#                   '","value": ', str(__VALUE),
#                   ',"message": ', __MSG_JSON, '}'
#                   ))


def test_minimum_blabber():
    assert __T_OUT.minimum_blabbers() == 3


def test_valid_blabber():
    pass


# def test_to_json():
#     s = __JSON
#     assert json.loads(msg.to_json()) == json.loads(s)
#
#
# def test_from_json():
#     s = __JSON
#     assert __MSG_JSON == __JSON
#     assert __T_OUT == Transactions.TransactionOutput.from_json(json.loads(s))
#
#
# def test__eq():
#     assert msg == msg1
