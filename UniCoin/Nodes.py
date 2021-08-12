import binascii
import json
import os
import threading
import uuid
import operator
import Crypto
import requests
import concurrent.futures
import queue
import time

from typing import List, Set, Dict
from Crypto.PublicKey import RSA
from Crypto.PublicKey.RSA import RsaKey
from Crypto.Signature import pkcs1_15
from Crypto.Signature.pkcs1_15 import PKCS115_SigScheme

import UniCoin.helpers.paths as paths
import UniCoin.Blockchain as Blockchain
import UniCoin.Transactions as Transactions

import logging
log = logging.getLogger('werkzeug')


class Peer:
	def __init__(self, address: str, port: int):
		"""
		Peer entity.
		Each peer is basically a node that we can send/receive information.
		:param address: IP Address of the peer
		:param port: Port of the peer
		"""
		self.address: str = address
		self.port: int = port

	def __str__(self):
		return f'{self.address}:{self.port}'

	def __hash__(self):
		return hash((self.address, self.port))

	def __eq__(self, other):
		if not isinstance(other, Peer):
			return NotImplemented

		return self.address == other.address and self.port == other.port


class PeerNetwork:
	"""
	Network of peers stored in each node.
	Handles registration/incoming messages etc.
	"""
	def __init__(self, my_peer: Peer = None):
		self._my_peer: Peer = my_peer
		self._peers = self.__load_peers()
		self.__transactions_queue = queue.Queue()
		self.__blocks_queue = queue.Queue()

		# Threads for "Async Handling" of transactions and blocks.
		# Threads are just a quick addition. They are not correctly made
		# and using infinite loops to work instead of an event system...

		self.__transactions_thread = threading.Thread(target=self.__handle_transactions, args=(), daemon=True)
		self.__transactions_thread.start()

		self.__blocks_thread = threading.Thread(target=self.__handle_blocks, args=(), daemon=True)
		self.__blocks_thread.start()

	def __load_peers(self) -> set:
		"""
		Load peers from file.
		:return: Set of available peers.
		"""
		peers = set()
		try:
			with open(f'{paths.FILE_NODELIST}', 'r') as file:
				data = json.load(file)
				for peer in data:
					address, port = str(peer).split(':')
					peers.add(Peer(
						address=address,
						port=int(port)
					))
				return json.load(file)
		except Exception:
			pass
		finally:
			if self._my_peer:
				try:
					peers.remove(self._my_peer)
				except Exception:
					pass
			return peers

	def __store_peers(self):
		"""
		Store peers to file.
		"""
		file_name = f'{paths.FILE_NODELIST}'
		os.makedirs(os.path.dirname(file_name), exist_ok=True)
		peers = self.peers.copy()

		if self._my_peer:
			peers.add(self._my_peer)

		with open(file_name, 'wb+') as file:
			data = json.dumps(list(map(lambda o: str(o), peers))).encode('utf-8')
			file.write(data)

	def register_peer(self, peer: Peer):
		"""
		Register peer if not already registered.
		:param peer:
		:return: If peer was registered or not.
		"""
		if peer in self.peers:
			return False

		self.peers.add(peer)
		self.__store_peers()
		return True

	@staticmethod
	def __post_json(url, data):
		"""
		:param url: sub_url of peer to call.
		:param data: json data to pass.
		:return: None if failure, otherwise the response text.
		"""
		try:
			response = requests.post(url, json=data)
			if response.status_code == 200:
				return response.text
			return None
		except Exception as e:
			return None

	def __broadcast_json(self, url, data):
		"""
		Broadcast a JSON Post to all peers.
		:param url: sub_url of peer to call.
		:param data: json data to pass.
		:return: Tuple containing successfully sent and total peers.
		"""
		total_peers = len(self.peers)
		with concurrent.futures.ThreadPoolExecutor() as executor:
			futures = [
				executor.submit(self.__post_json, f'http://{peer}/{url}', data) for peer in self.peers
			]
			total_sent = len(list(filter(lambda o: o is not None, [f.result() for f in futures])))

			return total_sent, total_peers

	def __handle_transactions(self):
		"""
		Thread handling all incoming transactions.
		"""
		q = self.__transactions_queue
		while True:
			if not q.empty():
				transaction: Transactions.Transaction = q.get(timeout=1)
				t_hash = transaction.hash
				log.debug(f'[TRANSACTION - {t_hash}] Broadcasting Transaction')
				data = transaction.to_json().decode('utf-8')
				if data is None:
					log.debug(f'[TRANSACTION - {t_hash}] Broadcasting Transaction failed. Bad JSON')
				total_sent, total_peers = self.__broadcast_json(f'api/broadcasts/new_transaction', data)

				log.debug(f'[TRANSACTION - {t_hash}] Broadcast ended. {total_sent}/{total_peers} peers received the message')
			time.sleep(1)

	def __handle_blocks(self):
		"""
		Thread handling all incoming transactions.
		"""
		q = self.__blocks_queue
		while True:
			if not q.empty():
				block: Blockchain.Block = q.get(timeout=1)
				b_hash = block.hash
				log.debug(f'[BLOCK - {b_hash}] Broadcasting Block')
				data = block.to_json().decode('utf-8')
				if data is None:
					log.debug(f'[BLOCK - {b_hash}] Broadcasting Block failed. Bad JSON')
				total_sent, total_peers = self.__broadcast_json(f'api/broadcasts/new_block', data)

				log.debug(f'[BLOCK - {b_hash}] Broadcast ended. {total_sent}/{total_peers} peers received the message')
			time.sleep(1)

	def broadcast_transaction(self, transaction: Transactions.Transaction):
		"""
		Add transaction in queue to be broadcasted.
		:param transaction:
		"""
		self.__transactions_queue.put(transaction)

	def broadcast_block(self, block: Blockchain.Block):
		self.__blocks_queue.put(block)

	def check_peer_chains(self, my_length: int):
		tmp_length = my_length
		tmp_chain = None
		for peer in self.peers:
			length = self.check_chain_length(peer)
			if length > tmp_length:
				blockchain = self.steal_blockchain(peer)
				if blockchain and blockchain.check_validity(lite=False):
					tmp_chain = blockchain
					tmp_length = tmp_chain.size
					log.debug(f'[PEER] Found bigger valid chain from \'{peer}\'.')

		return tmp_chain

	@staticmethod
	def check_chain_length(peer: Peer) -> int:
		"""
		:param peer:
		:return: Length of peer's blockchain.
		"""
		try:
			response = requests.get(f'http://{peer}/api/blockchain/length')

			if response.status_code == 200:
				json_data = json.loads(response.text)
				return json_data["length"]
		except Exception:
			log.debug(f'[PEER] Failed fetching blockchain length from peer {peer}')
			return 0
		return 0

	@staticmethod
	def steal_blockchain(peer: Peer) -> Blockchain.BlockChain:
		"""
		Grab the chain, validate it and if everything is good, swap it with ours.
		:param peer:
		:return:
		"""
		response = requests.get(f'http://{peer}/api/blockchain/chain')

		if response.status_code == 200:
			try:
				return Blockchain.BlockChain.from_json(json.loads(response.text))
			except Exception:
				log.debug(f'[PEER] Failed fetching blockchain from peer {peer}')
				return None
		return None

	@property
	def peers(self):
		return self._peers


class Node:
	TYPE_CLIENT = 0
	TYPE_MINER = 1

	def __init__(self, private_key: RsaKey, my_peer=None):
		self.network: PeerNetwork = PeerNetwork(
			my_peer=my_peer
		)
		self.blockchain = Blockchain.BlockChain()
		self.private_key: RsaKey = private_key
		self.public_key: RsaKey = self.private_key.publickey()
		self.processed_hashes: List[str] = list()  # Keep track of already processed
												   # blocks and transactions

	@property
	def identity(self) -> str:
		"""
		ASCII Representation of node's public_key
		:return:
		"""
		return binascii.hexlify(self.public_key.exportKey(format='DER')).decode('ascii')

	def __str__(self):
		return self.identity


class Client(Node):
	# def __init__(self, private_key: RsaKey, my_peer=None):
	# 	super().__init__(private_key, my_peer=my_peer)
		# self.signer: PKCS115_SigScheme = pkcs1_15.new(self.private_key)
		# self.my_UTXOs: Set[Transactions.TransactionInput] = set()  # List of unspent transactions

	@property
	def balance(self):
		return sum(
			filter(lambda o: o > 0, [utxo.balance for utxo in self.my_UTXOs])
		)

	def send_coins(self, transactions: list) -> bool:
		transaction_outputs: List[Transactions.TransactionOutput] = []
		total_balance = 0
		allocated_balance = 0
		# Create Transaction Outputs
		for t in transactions:
			try:
				if isinstance(t[0], str) and isinstance(t[1], int) and t[1] > 0:
					transaction_outputs.append(
						Transactions.TransactionOutput(
							recipient_address=t[0],
							value=t[1]
						)
					)
					total_balance += t[1]
			except Exception:
				log.error('Failed parsing transactions. Wrong tuple provided.')
				return False

		# Allocate enough funds
		sorted_utxo: List[Transactions.TransactionInput] = sorted(self.my_UTXOs, key=operator.attrgetter('balance'))
		selected_utxo: List[Transactions.TransactionInput] = []
		for utxo in sorted_utxo:
			if allocated_balance >= total_balance:
				break

			if utxo.balance == -1:
				continue

			selected_utxo.append(utxo)
			allocated_balance += utxo.balance

		# Verify we have enough funds
		if total_balance > allocated_balance:
			return False

		transaction = Transactions.Transaction(
			sender=self.identity,
			inputs=tuple(selected_utxo),
			outputs=tuple(transaction_outputs),
		)
		transaction.sign_transaction(self)

		if isinstance(self, Miner):
			self.add_transaction(transaction)

		# Set UTXO as temporary 'Spent'
		for utxo in selected_utxo:
			self.my_UTXOs.remove(utxo)

		self.network.broadcast_transaction(transaction)
		return True


class Miner(Client):
	def __init__(self, private_key: RsaKey, my_peer=None):
		# super().__init__(private_key, my_peer=my_peer)
		# self.verified_transactions: Dict[str, Transactions.Transaction] = dict()  # Store Verified transactions to input in block
		# # self.UTXOs: Set[Transactions.TransactionInput] = set()  # List of Unspent Transactions Available

		# Unconventional, but i guess it's fine just for the demonstration
		# Miner shouldn't create Genesis block?
		self.__construct_genesis()

		# Settings
		self.__is_mining: bool = False
		self.__mining_thread = threading.Thread(target=self.__mine, daemon=True)

	def __construct_genesis(self):
		self.construct_block(
			proof=42,
			previous_hash="Samira-mira-mira-e-e-Waka-Waka-e-e"
		)

	def construct_block(self, verified_transactions: List[Transactions.Transaction] = [],
						proof=None, previous_hash=None) -> Blockchain.Block:
		if proof is None or previous_hash is None:
			last_block = self.blockchain.last_block
			proof = Blockchain.proof_of_work(last_block.proof)
			previous_hash = last_block.calculate_hash()

		block = Blockchain.Block(
			index=len(self.blockchain.blocks),
			proof=proof,
			verified_transactions=verified_transactions,
			previous_block_hash=previous_hash)

		coinbase_total = block.reward + sum([trans.transaction_fee for trans in verified_transactions])

		# Coinbase Transaction
		coinbase = Transactions.Transaction(
			outputs=tuple([
				Transactions.TransactionOutput(
					self.identity,
					coinbase_total
				)]
			)
		)
		coinbase.sign_transaction(self)
		block.verified_transactions.insert(0, coinbase)
		self.network.broadcast_block(block)	 # Broadcast block to available nodes

		self.blockchain.blocks.append(block)

		# -- Add Coinbase as new UTXO for Miner --
		# utxo = Transactions.TransactionInput(
		# 		block.index, 0, 0, coinbase_total
		# 	)

		# utxo.check_validity(self.identity, self.blockchain.blocks)
		# self.my_UTXOs.add(utxo)  # Add UTXO

		# ----------------------------------
		# -- Add all Outputs as new UTXOS --
		# ----------------------------------
		self.blockchain.UTXOs.difference_update(block.extract_STXOs())
		self.blockchain.UTXOs = set(self.blockchain.UTXOs.union(block.extract_UTXOs()))

		# -- UPDATE MY UTXO SET --
		my_utxos = set(block.find_UTXOs(self.identity))
		for my_utxo in my_utxos:  # This will fail, but will cache the value
			my_utxo.check_validity(sender=None, blockchain=self.blockchain)
		self.my_UTXOs = self.my_UTXOs.union(my_utxos)
		# ---------------------

		return block

	@property
	def is_mining(self):
		return self.__is_mining

	def toggle_mining(self, mine: bool = None):
		self.__is_mining = not self.__is_mining if mine is None else mine

		if self.__is_mining:
			self.__mining_thread.start()
		else:
			self.__mining_thread = threading.Thread(target=self.__mine, daemon=True)

	def __mine(self):
		while self.__is_mining:
			self.manual_mine()

	def manual_mine(self):
		"""
		Mine --WITHOUT TRANSACTION LIMIT--
		:return:
		"""
		if not self.verified_transactions:
			return False

		transactions: Dict[str, Transactions.Transaction] = self.verified_transactions
		self.verified_transactions = dict()
		new_block = self.construct_block(
			verified_transactions=list(transactions.values()),
		)
		return new_block

	def add_transaction(self, transaction) -> bool:
		if not isinstance(transaction, Transactions.Transaction):
			raise ValueError("Transaction is not a valid Transaction object!")

		t_hash = transaction.hash
		if t_hash in self.verified_transactions.keys():
			return False

		if not transaction.check_validity(blockchain=self.blockchain, check_utxos=True):
			return False

		self.verified_transactions[t_hash] = transaction
		return True

#
# class KeyFactory:
# 	"""
# 	Manages creating, storing or loading UniCoin Clients.
# 	"""
#
# 	@staticmethod
# 	def create_key() -> RsaKey:
# 		random = Crypto.Random.new().read
# 		return RSA.generate(1024, random)
#
# 	@staticmethod
# 	def store_key(key: RsaKey, friendly_name: str = None):
# 		if not isinstance(key, RsaKey):
# 			raise ValueError('First argument must be an RsaKey!')
#
# 		name = friendly_name if friendly_name else str(uuid.uuid4())
# 		file_name = f'{paths.PATH_WALLETS}/{name}.der'
# 		os.makedirs(os.path.dirname(file_name), exist_ok=True)
# 		with open(file_name, 'wb+') as file:
# 			file.write(key.exportKey(format='DER'))
#
# 	@staticmethod
# 	def load_key(name: str) -> RsaKey:
# 		with open(f'{paths.PATH_WALLETS}/{name}.der', 'rb') as file:
# 			key = file.read()
#
# 		return RSA.import_key(key)
