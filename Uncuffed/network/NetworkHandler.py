import json
import queue
import threading
import time
from typing import Optional

import requests

import Uncuffed.transactions as Transactions
import Uncuffed.chain as Chain

from Uncuffed import log
from .PeerNetwork import PeerNetwork
from .Peer import Peer

import Uncuffed.web.routes


class NetworkHandler:
    __instance = None

    def __init__(self, my_peer: Peer):
        if NetworkHandler.__instance is not None:
            raise Exception('This class is a singleton!')
        else:
            NetworkHandler.__instance = self

        self.my_peer = my_peer
        self.network: PeerNetwork = PeerNetwork.get_instance()
        self.__transactions_queue = queue.Queue()
        self.__blocks_queue = queue.Queue()

        # Threads for "Async Handling" of transactions and blocks.
        # Threads are just a quick addition. They are not correctly made
        # and using infinite loops to work instead of an event system...

        self.__transactions_thread = threading.Thread(target=self.__handle_transactions, args=(), daemon=True)
        self.__transactions_thread.start()

        self.__blocks_thread = threading.Thread(target=self.__handle_blocks, args=(), daemon=True)
        self.__blocks_thread.start()

    @classmethod
    def get_instance(cls, my_peer: Peer = None):
        if cls.__instance is None:
            if my_peer is None:
                raise Exception('Singleton class must first be initialized with a Peer object')
            else:
                NetworkHandler(my_peer=my_peer)

        return cls.__instance

    def broadcast_transaction(self, transaction: Transactions.Transaction):
        """
        Add transaction in queue to be broadcasted.
        :param transaction:
        """
        self.__transactions_queue.put(transaction)

    def broadcast_block(self, block: Chain.Block):
        """
        Add block in queue to be broadcasted.
        :param block:
        """
        self.__blocks_queue.put(block)

    def __handle_transactions(self):
        """
        Thread handling all incoming transactions.
        """
        q = self.__transactions_queue
        while True:
            if not q.empty():
                transaction: Transactions.Transaction = q.get(timeout=1)
                t_hash = transaction.hash
                data = transaction.to_json().decode('utf-8')

                log.debug(f'[TRANSACTION - {t_hash}] Broadcasting Transaction')

                if data is None:
                    log.warn(f'[TRANSACTION - {t_hash}] Broadcasting Transaction failed. Bad JSON')

                total_sent, total_peers = self.network.broadcast_json(
                    caller=self.my_peer,
                    route=Uncuffed.web.routes.API_BROADCASTS_NEW_TRANSACTION,
                    data=data
                )

                log.debug(
                    f'[TRANSACTION - {t_hash}] Broadcast ended. {total_sent}/{total_peers} peers received the message')
            time.sleep(1)

    def __handle_blocks(self):
        """
        Thread handling all incoming transactions.
        """
        q = self.__blocks_queue
        while True:
            if not q.empty():
                block: Chain.Block = q.get(timeout=1)
                log.debug(f'[BLOCK - {block.height}] Broadcasting Block')
                data = block.to_json().decode('utf-8')
                if data is None:
                    log.warn(f'[BLOCK - {block.height}] Broadcasting Block failed. Bad JSON')
                total_sent, total_peers = self.network.broadcast_json(
                    caller=self.my_peer,
                    route=Uncuffed.web.routes.API_BROADCASTS_NEW_BLOCK,
                    data=data
                )

                log.debug(f'[BLOCK - {block.height}] Broadcast ended. {total_sent}/{total_peers} peers received the message')
            time.sleep(1)

    def check_peer_chains(self, my_length: int):
        max_length = my_length
        max_chain = None

        for peer in self.network.get_peers(exclude_peer=self.my_peer):
            length = self.check_chain_length(peer)
            if length > max_length:
                blockchain = self.steal_blockchain(peer)
                if blockchain and blockchain.is_valid(lite=False):
                    max_chain = blockchain
                    max_length = max_chain.size

                    log.info(f'[PEER] Found bigger valid chain from \'{peer}\'.')

        return max_chain

    @staticmethod
    def check_chain_length(peer: Peer) -> int:
        """
        :param peer:
        :return: Length of peer's blockchain.
        """
        try:
            response = requests.get(f'{peer.get_url()}{Uncuffed.web.routes.API_BLOCKCHAIN_LENGTH}')

            if response.status_code == 200:
                json_data = json.loads(response.text)
                return json_data['length']
        except Exception:
            log.warn(f'[PEER] Failed fetching blockchain length from peer {peer}')
            return 0
        return 0

    @staticmethod
    def steal_blockchain(peer: Peer) -> Optional[Chain.Blockchain]:
        """
        Grab the chain, validate it and if everything is good, swap it with ours.
        :param peer:
        :return:
        """
        response = requests.get(f'{peer.get_url()}{Uncuffed.web.routes.API_BLOCKCHAIN}')

        if response.status_code == 200:
            try:
                return Chain.Blockchain.from_json(json.loads(response.text))
            except Exception:
                log.warn(f'[PEER] Failed fetching blockchain from peer {peer}')
                return None
        return None
