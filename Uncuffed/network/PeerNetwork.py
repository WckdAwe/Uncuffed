import collections
import concurrent
import json
import requests as requests


from typing import Set, Optional
from .Peer import Peer
from ..helpers.Storable import Storable
from ..helpers.paths import PATH_DATA


class PeerNetwork(Storable):
    """
    Network of peers stored in each node.
    """

    __instance = None

    def __init__(self, peers: Set[Peer] = None):
        """ Virtually private constructor. """
        if PeerNetwork.__instance is not None:
            raise Exception('This class is a singleton!')
        else:
            PeerNetwork.__instance = self
            self._peers = peers or set()
            self._my_peer: Optional[Peer] = None

    @classmethod
    def get_instance(cls):
        if cls.__instance is None:
            return cls.load_from_file()
        else:
            return cls.__instance

    def get_peers(self, exclude_peer: Peer = None):
        """
        :return: A copy of the peers set.
        """
        peer_set = set(self._peers)

        if exclude_peer is not None:
            peer_set.remove(exclude_peer)
        return set(self._peers)

    def register_peer(self, peer: Peer):
        """
        Register peer if not already registered.
        :param peer:
        :return: If peer was registered or not.
        """
        if peer in self._peers:
            return False

        self._peers.add(peer)
        self.store_to_file()
        return True

    def unregister_peer(self, peer: Peer):
        """
        Unregister peer if it is registered
        :param peer:
        :return: If peer was registered or not.
        """
        if peer not in self._peers:
            return False

        self._peers.remove(peer)
        self.store_to_file()
        return True

    @staticmethod
    def post_json(peer: Peer, route, data):
        """
        :param peer: The peer.
        :param route: sub_url of peer to call.
        :param data: json data to pass.
        :return: None if failure, otherwise the response text.
        """
        try:
            url = peer.get_url() + route
            response = requests.post(url=url, json=data)
            if response.status_code == 200:
                return response.text
            return None
        except Exception as e:  # TODO
            return None

    def broadcast_json(self, caller: Peer, route: str, data):
        """
        Broadcast a JSON Post to all peers.
        :param caller: Peer initiating broadcast
        :param route: sub_url of peer to call.
        :param data: json data to pass.
        :return: Tuple containing successfully sent and total peers.
        """
        peers = self.get_peers
        peers.remove(caller)
        total_peers = len(peers)

        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [
                executor.submit(self.post_json, peer, route, data) for peer in peers
            ]
            total_sent = len(list(filter(lambda o: o is not None, [f.result() for f in futures])))

            return total_sent, total_peers

    @staticmethod
    def get_storage_location() -> str:
        return f'{PATH_DATA}/node_list.json'

    @classmethod
    def from_json(cls, data):
        peers = set(map(Peer.from_string, data))

        return cls(
            peers=peers,
        )

    def to_json(self, **args) -> bytes:
        return json.dumps(list(map(lambda o: str(o), self._peers)), **args).encode('utf-8')

    def to_dict(self) -> dict:
        return collections.OrderedDict({
            'peers': map(lambda o: str(o), self._peers),
        })
