import operator

from typing import List

import logging
log = logging.getLogger('werkzeug')

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