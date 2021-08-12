# import hashlib
# import json
# import collections
# import time

# import UniCoin.Transactions as Transactions
#
# from typing import List, Tuple, Set
# from Crypto.Hash import SHA256
#
# import logging
#
# log = logging.getLogger('werkzeug')

#
# def verify_proof(prev_proof, proof, difficulty=2) -> bool:
#     """
# 	Verifying if the Proof-of-Work is correct, based on a specific difficulty.
# 	:param prev_proof: Proof-of-Work of previous block.
# 	:param proof: Proof-of-Work that is to be checked.
# 	:param difficulty: Difficulty level that is to be checked.
# 	:return: Whether the Proof-of-Work found is valid or not.
# 	"""
#     if difficulty <= 0:
#         raise ValueError("Difficulty must be a positive number!")
#
#     guess = f'{prev_proof}{proof}'.encode()
#     guess_hash = SHA256.new(guess).hexdigest()
#     return guess_hash[:difficulty] == "1" * difficulty
#
#
# def proof_of_work(prev_proof: int, difficulty=2) -> int:
#     """
# 	Proof-of-Work algorithm. Increment a random number and trying to verify it
# 	each time until Proof-of-work returns True.
# 	:param prev_proof: Proof-of-Work of previous block.
# 	:param difficulty: Difficulty level of mining.
# 	:return:
# 	"""
#     proof = 0
#     while verify_proof(prev_proof, proof, difficulty) is False:
#         proof += 1
#
#     return proof


class Block:
    # """
	# Block Instance
	# ------------------
	# A single block of the blockchain, containing the proof-of-work of the previous block alongside with the
	# verified transactions.
	# """
    #
    # def __init__(self, index, proof=0, verified_transactions=None, previous_block_hash: str = None,
    #              timestamp: float = None):
    #     self.index: int = index
    #     self.proof: int = proof
    #     self.verified_transactions: List[Transactions.Transaction] = verified_transactions or []
    #     self.previous_block_hash: str = previous_block_hash
    #     self.timestamp: float = timestamp or time.time()

    # def check_validity(self, prev_block, lite=True, blockchain=None) -> bool:
        # """
		# :param prev_block:
		# :param lite: Whether the client is Lite or not (Client or Miner).
		# :argument blockchain: Blockchain must be provided if checking for non-lite validity.
		# :return: Whether the block is valid or not
		# """
        # if not isinstance(prev_block, Block):
        #     return False
        # elif prev_block.index + 1 != self.index:
        #     log.debug(f'[BLOCK - {self.hash}] Verification Failure (BLOCK ORDER)')
        #     return False
        # elif prev_block.calculate_hash() != self.previous_block_hash:
        #     log.debug(f'[BLOCK - {self.hash}] Verification Failure (HASH)')
        #     return False
        # elif len(self.verified_transactions) == 0 and self.index != 0:
        #     log.debug(f'[BLOCK - {self.hash}] Verification Failure (NO VERIFIED TRANSACTIONS)')
        #     return False
        # elif self.timestamp <= prev_block.timestamp:
        #     log.debug(f'[BLOCK - {self.hash}] Verification Failure (TIMESTAMP)')
        #     return False
        # elif not verify_proof(prev_block.proof, self.proof):
        #     log.debug(f'[BLOCK - {self.hash}] Verification Failure (PROOF)')
        #     return False
        # elif not self._verify_coinbase(lite=True):  # Lite verification of coinbase (No need to check each transaction)
        #     log.debug(f'[BLOCK - {self.hash}] Verification Failure (COINBASE LITE)')
        #     return False
        # else:
        #     if not lite:
        #         # Verify each transaction that is valid
        #         for indx in range(0, len(self.verified_transactions)):
        #             trans = self.verified_transactions[indx]
        #             is_coinbase = True if indx == 0 else False
        #             if not trans.check_validity(blockchain=blockchain, is_coinbase=is_coinbase):
        #                 log.debug(f'[BLOCK - {self.hash}] Verification Failure (TRANSACTION INVALID)')
        #                 return False
        #
        #         if not self._verify_coinbase(lite=True):
        #             log.debug(f'[BLOCK - {self.hash}] Verification Failure (COINBASE)')
        #             return False
        #
        #     return True

    # def _verify_coinbase(self, lite=False) -> bool:
    #     coinbase = self.verified_transactions[0]
    #     if lite:
    #         return coinbase.balance_output >= self.reward
    #     else:
    #         trans_fees = [trans.transaction_fee for trans in self.verified_transactions]
    #         return trans_fees == coinbase.balance_output

    # def calculate_hash(self) -> str:
    #     """
	# 	Returns the hash of the block by converting its instance into a JSON String.
	# 	:return: Hash of the block
	# 	"""
    #     return SHA256.new(self.to_json()).hexdigest()

    # @property
    # def reward(self) -> int:
    #     """
	# 	Reduce block reward by 5 per 4 mining operations.
	# 	Total coins in circulation should be 1050
	# 	:return:
	# 	"""
    #     return max([0, 50 - 5 * ((self.index + 1) // 4)])

    # @property
    # def hash(self) -> str:
    #     return hashlib.md5(self.to_json()).hexdigest()

    def extract_UTXOs(self) -> set():
        resp = set()
        for t_indx, transaction in enumerate(self.verified_transactions):
            outputs: Tuple[Transactions.TransactionOutput] = transaction.outputs
            for o_indx, output in enumerate(outputs):
                utxo: Transactions.TransactionInput = Transactions.TransactionInput(
                    block_index=self.index,
                    transaction_index=t_indx,
                    output_index=o_indx
                )
                resp.add(utxo)
        return resp

    def extract_STXOs(self) -> set():
        resp = set()
        for t_indx, transaction in enumerate(self.verified_transactions):
            inputs: Tuple[Transactions.TransactionInput] = transaction.inputs
            for i_indx, inp in enumerate(inputs):
                resp.add(inp)
        return resp

    def find_UTXOs(self, address: str) -> set():
        resp = set()
        for t_indx, transaction in enumerate(self.verified_transactions):
            outputs: Tuple[Transactions.TransactionOutput] = transaction.outputs
            for o_indx, output in enumerate(outputs):
                if output.recipient_address == address:
                    utxo: Transactions.TransactionInput = Transactions.TransactionInput(
                        block_index=self.index,
                        transaction_index=t_indx,
                        output_index=o_indx
                    )
                    resp.add(utxo)
        return resp

    # def to_dict(self):
    #     return collections.OrderedDict({
    #         'index': self.index,
    #         'proof': self.proof,
    #         'transactions': list(map(lambda o: o.to_dict(), self.verified_transactions)),
    #         'previous_hash': self.previous_block_hash,
    #         'timestamp': self.timestamp})

    # def to_json(self, indent=None):
    #     return json.dumps(self.to_dict(), sort_keys=True, indent=indent).encode('utf-8')

    # @classmethod
    # def from_json(cls, data):
    #     index = int(data['index'])
    #     proof = int(data['proof'])
    #     verified_transactions = list(map(Transactions.Transaction.from_json, data['transactions']))
    #     previous_block_hash = str(data['previous_hash'])
    #     timestamp = float(data['timestamp'])
    #
    #     return cls(
    #         index=index,
    #         proof=proof,
    #         verified_transactions=verified_transactions,
    #         previous_block_hash=previous_block_hash,
    #         timestamp=timestamp
    #     )
    #
    # def __repr__(self):
    #     return self.to_json()
    #
    # def __str__(self):
    #     return str(self.to_json(indent=4).decode('utf-8'))


class BlockChain:
    """
	BlockChain
	------------------
	The BlockChain. ¯\_(ツ)_/¯
	"""

    def __init__(self, blocks=None, utxos=None):
        # self.blocks: List[Block] = blocks or []
        self.UTXOs: Set[Transactions.TransactionInput] = utxos or set()

    # @property
    # def last_block(self) -> Block:
    #     return self.blocks[-1]
    #
    # @property
    # def size(self) -> int:
    #     return len(self.blocks)

    # def check_validity(self, lite=False) -> bool:
    #     """
	# 	:return: Whether the Blockchain is valid or not.
	# 	"""
    #     block = self.last_block
    #     while block.index >= 1:
    #         prev_block = self.blocks[block.index - 1]
    #         if not block.check_validity(prev_block=prev_block, blockchain=self, lite=lite):
    #             log.debug(f'[BLOCKCHAIN] Block indx \'{block.index}\' is invalid.')
    #             return False
    #         block = prev_block
    #
    #     return True
    #
    # def to_dict(self):
    #     return collections.OrderedDict({
    #         'length': self.size,
    #         'chain': tuple(map(lambda o: o.to_dict(), self.blocks)),
    #         'utxos': tuple(map(lambda o: o.to_dict(), self.UTXOs))
    #     })

    # def to_json(self, indent=None):
    #     return json.dumps(self.to_dict(), sort_keys=True, indent=indent).encode('utf-8')

    # @classmethod
    # def from_json(cls, data):
    #     blocks = list(map(Block.from_json, data['chain']))
    #     utxos = set(map(Transactions.TransactionInput.from_json, data['utxos']))
    #
    #     return cls(
    #         blocks=blocks,
    #         utxos=utxos
    #     )

    @classmethod
    def find_block_diff(cls, old_blocks: List[Block], new_blocks: List[Block]) -> List[int]:
        if len(new_blocks) <= len(old_blocks):
            raise Exception("New chain is smaller or equal to old chain")

        diff = []
        for indx in range(0, len(old_blocks)):
            old_block = old_blocks[indx]
            new_block = new_blocks[indx]

            if old_block.hash != new_block.hash:
                diff.append(old_block.index)

        if len(diff) == 0:
            raise Exception("Difference is 0?? How?")
        return diff

    # def __repr__(self):
    #     return self.to_json()
    #
    # def __str__(self):
    #     return str(self.to_json(indent=4).decode('utf-8'))
