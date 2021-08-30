# from Uncuffed.helpers import JSONSerializable
# import Uncuffed.messages as Messages
# import Uncuffed.nodes as Nodes
#
#
# class Message(JSONSerializable):
#
#     def __init__(self, sender: str, message: Messages.AMessage):
#         self.sender: str = sender
#         self.__message: Messages.AMessage = message
#
#     def get_message(self, node: Nodes.ANode) -> Messages.AMessage:
#         if self.__message.message_type is Messages.EMessageType.PLAINTEXT or \
#             self.__message.message_type is Messages.EMessageType.PLAIN_IMAGE:
#             return self.__message
#
#         if self.sender == node.identity:    # Decrypt my Message
#             pass
#
#
#     @classmethod
#     def from_json(cls, data):
#         pass
#
#     def to_dict(self) -> dict:
#         pass