import json
import Uncuffed.transactions as Transactions
import Uncuffed.chain as Chain
import Uncuffed.nodes as Nodes
from flask import request

from Uncuffed import app, log
from Uncuffed.network import NetworkHandler
from ..routes import API_BROADCASTS_NEW_BLOCK, API_BROADCASTS_NEW_TRANSACTION
from ..decorators import requires_auth

n_handler: NetworkHandler = NetworkHandler.get_instance()


@app.route(API_BROADCASTS_NEW_BLOCK, methods=['POST'])
@requires_auth()
def broadcasts_new_block():
	"""
	:return:
	"""
	from Uncuffed import my_node

	json_data = request.get_json()
	if not json_data:
		return json.dumps({
			'message': 'Incorrect JSON Data.'
		}), 400

	data = json.loads(json_data)
	block = Chain.Block.from_json(data)

	if block.hash in my_node.processed_hashes:
		return json.dumps({
			'message': 'Already processed',
		})
	else:
		my_node.processed_hashes.append(block.hash)

	log.debug(f'[BLOCK - {block.height}] Received')

	if my_node.blockchain.size != 0 and block.is_valid(
			prev_block=my_node.blockchain.last_block,
			lite=False if isinstance(my_node, Nodes.Miner) else True,
			blockchain=my_node.blockchain
	):
		log.debug(f'[BLOCK - {block.height}] Validated')
		my_node.blockchain.blocks.append(block)

		# -- UPDATE UTXO SET --
		my_node.blockchain.UTXOs.difference_update(block.extract_STXOs())
		my_node.blockchain.UTXOs = set(my_node.blockchain.UTXOs.union(block.extract_UTXOs()))
		# ---------------------

		# -- UPDATE MY UTXO SET --
		my_utxos = block.find_UTXOs(my_node.identity)  # Find UTXOs belonging to me
		my_node.my_UTXOs = my_node.my_UTXOs.union(my_utxos)  # Union them with existing UTXOs belonging to me
		my_node.my_UTXOs.intersection_update(my_node.blockchain.UTXOs)  # Update my list based on Blockchain UTXOs

		for my_utxo in my_node.my_UTXOs:  # Cache UTXO balances
			my_utxo.get_balance(blockchain=my_node.blockchain)
		# ---------------------

		# -- REMOVE (NOW) INVALID TRANSACTIONS --
		for trans in block.transactions:
			my_node.verified_transactions.pop(trans.hash, None)
		# ---------------------------------------
		n_handler.broadcast_block(block)

		if isinstance(my_node, Nodes.Client):
			my_node.blockchain.blocks[block.height].clean_transactions()

	# Block is INVALID
	else:

		# Other chain might be AHEAD
		if my_node.blockchain.size == 0 or \
			block.height > my_node.blockchain.last_block.height + 1:

			log.debug(f'[BLOCK - {block.height}] Rejected (AHEAD)')
			chain = n_handler.check_peer_chains(my_node.blockchain.size)
			if chain:  # FETCHED BIGGER VALID CHAIN (INCLUDING UTXOs)
				log.debug('[BLOCKCHAIN] Fetched bigger valid chain.')

				# -- FIND DIFFERENT BLOCKS --
				diff = Chain.Blockchain.find_block_diff(
					old_blocks=my_node.blockchain.blocks,
					new_blocks=chain.blocks
				)

				# 2 Different for loops just in case a UTXO has just changed it's block
				# position.

				# Remove OLD UTXOs
				for indx in diff:

					# -- REMOVE OLD MY_UTXOS --
					tmp_block: Chain.Block = my_node.blockchain.blocks[indx]
					old_utxos = tmp_block.find_UTXOs(my_node.identity)
					my_node.my_UTXOs.difference_update(old_utxos)

					if isinstance(my_node, Nodes.Miner):
						# -- COLLECT VALID TRANSACTIONS from our rejected block --
						for t_indx in range(1, len(tmp_block.transactions)):
							trans = tmp_block.transactions[t_indx]
							my_node.verified_transactions[trans.hash] = trans

				if len(diff) == 0:  # Just in case the Client has no block knowledge
					diff.append(0)

				# Add new UTXOs
				for indx in range(diff[0], len(chain.blocks)):
					tmp_block: Chain.Block = chain.blocks[indx]
					new_utxos = tmp_block.find_UTXOs(my_node.identity)
					my_node.my_UTXOs = my_node.my_UTXOs.union(new_utxos)

					if isinstance(my_node, Nodes.Miner):
						# -- REMOVE TRANSACTIONS that are already in the block --
						for t_indx in range(1, len(tmp_block.transactions)):
							trans = tmp_block.transactions[t_indx]
							my_node.verified_transactions.pop(trans.hash, None)
				# ---------------------

				my_node.blockchain = chain
				my_node.my_UTXOs.intersection_update(my_node.blockchain.UTXOs)  # Should solve above issue? TODO
				for my_utxo in my_node.my_UTXOs:
					my_utxo.get_balance(blockchain=my_node.blockchain)

				for block in my_node.blockchain.blocks:
					block.clean_transactions()
			else:
				log.info(f'[BLOCK - {block.height}] Rejected (AHEAD - NO KNOWLEDGE)')
		else:
			log.info(f'[BLOCK - {block.height}] Rejected (INVALID)')

	return json.dumps({
		'message': 'ok',
	})


# @app.route(API_BROADCASTS_NEW_BLOCK, methods=['POST'])
# @requires_auth()
# def broadcasts_new_block():
# 	"""
# 	:return:
# 	"""
# 	from Uncuffed import my_node
#
# 	json_data = request.get_json()
# 	if not json_data:
# 		return json.dumps({
# 			'message': 'Incorrect JSON Data.'
# 		}), 400
#
# 	data = json.loads(json_data)
# 	block = Chain.Block.from_json(data)
#
# 	if block.hash in my_node.processed_hashes:
# 		return json.dumps({
# 			'message': 'Already processed',
# 		})
# 	else:
# 		my_node.processed_hashes.append(block.hash)
#
# 	log.debug(f'[BLOCK - {block.height}] Received')
# 	if isinstance(my_node, Nodes.Miner):
# 		# BLOCK is valid
# 		if block.is_valid(
# 				prev_block=my_node.blockchain.last_block,
# 				lite=False,
# 				blockchain=my_node.blockchain
# 		):
# 			log.debug(f'[BLOCK - {block.height}] Validated')
# 			my_node.blockchain.blocks.append(block)
#
# 			# -- UPDATE UTXO SET --
# 			my_node.blockchain.UTXOs.difference_update(block.extract_STXOs())
# 			my_node.blockchain.UTXOs = set(my_node.blockchain.UTXOs.union(block.extract_UTXOs()))
# 			# ---------------------
#
# 			# -- UPDATE MY UTXO SET --
# 			my_utxos = block.find_UTXOs(my_node.identity)						# Find UTXOs belonging to me
# 			my_node.my_UTXOs = my_node.my_UTXOs.union(my_utxos)					# Union them with existing UTXOs belonging to me
# 			my_node.my_UTXOs.intersection_update(my_node.blockchain.UTXOs)		# Update my list based on Blockchain UTXOs
#
# 			for my_utxo in my_node.my_UTXOs:									# Cache UTXO balances
# 				my_utxo.get_balance(blockchain=my_node.blockchain)
# 			# ---------------------
#
# 			# -- REMOVE (NOW) INVALID TRANSACTIONS --
# 			for trans in block.transactions:
# 				my_node.verified_transactions.pop(trans.hash, None)
# 			# ---------------------------------------
# 			n_handler.broadcast_block(block)
#
# 		# Block is INVALID
# 		else:
#
# 			# Other chain might be AHEAD
# 			if block.height > my_node.blockchain.last_block.height + 1:
# 				log.debug(f'[BLOCK - {block.height}] Rejected (AHEAD)')
# 				chain = n_handler.check_peer_chains(my_node.blockchain.size)
# 				if chain:  # FETCHED BIGGER VALID CHAIN (INCLUDING UTXOs)
# 					log.debug('[BLOCKCHAIN] Fetched bigger valid chain.')
#
# 					# -- FIND DIFFERENT BLOCKS --
# 					diff = Chain.Blockchain.find_block_diff(
# 						old_blocks=my_node.blockchain.blocks,
# 						new_blocks=chain.blocks
# 					)
#
# 					# 2 Different for loops just in case a UTXO has just changed it's block
# 					# position.
#
# 					# Remove OLD UTXOs
# 					for indx in diff:
#
# 						# -- REMOVE OLD MY_UTXOS --
# 						tmp_block: Chain.Block = my_node.blockchain.blocks[indx]
# 						old_utxos = tmp_block.find_UTXOs(my_node.identity)
# 						my_node.my_UTXOs.difference_update(old_utxos)
#
# 						# -- COLLECT VALID TRANSACTIONS from our rejected block --
# 						for t_indx in range(1, len(tmp_block.transactions)):
# 							trans = tmp_block.transactions[t_indx]
# 							my_node.verified_transactions[trans.hash] = trans
#
# 					# Add new UTXOs
# 					for indx in range(diff[0], len(chain.blocks)):
# 						tmp_block: Chain.Block = chain.blocks[indx]
# 						new_utxos = tmp_block.find_UTXOs(my_node.identity)
# 						my_node.my_UTXOs = my_node.my_UTXOs.union(new_utxos)
#
# 						# -- REMOVE TRANSACTIONS that are already in the block --
# 						for t_indx in range(1, len(tmp_block.transactions)):
# 							trans = tmp_block.transactions[t_indx]
# 							my_node.verified_transactions.pop(trans.hash, None)
# 					# ---------------------
#
# 					my_node.blockchain = chain
# 					my_node.my_UTXOs.intersection_update(my_node.blockchain.UTXOs)  # Should solve above issue? TODO
# 					for my_utxo in my_node.my_UTXOs:
# 						my_utxo.get_balance(blockchain=my_node.blockchain)
# 			else:
# 				log.debug(f'[BLOCK - {block.height}] Rejected (INVALID)')
# 	elif type(my_node) is Nodes.Client:
# 		log.debug(f'[BLOCK - {block.height}] ECHOING')
# 		if my_node.blockchain.size != 0 and block.is_valid(
# 				prev_block=my_node.blockchain.last_block,
# 				blockchain=my_node.blockchain,
# 				lite=True):
# 			my_node.blockchain.blocks.append(block)
#
# 			# -- UPDATE MY UTXO SET --
# 			my_utxos = set(block.find_UTXOs(my_node.identity))
# 			my_node.my_UTXOs = my_node.my_UTXOs.union(my_utxos)
# 			my_node.my_UTXOs.intersection_update(my_node.blockchain.UTXOs)  # Client doesn't have blockchain UTXOS!
# 			n_handler.broadcast_block(block)  # Echo Transaction
#
# 		else:
# 			# Other chain might be AHEAD
# 			if my_node.blockchain.size == 0 or \
# 				block.height > my_node.blockchain.last_block.height + 1:
#
# 				log.debug(f'[BLOCK - {block.height}] Rejected (AHEAD)')
# 				chain = n_handler.check_peer_chains(my_node.blockchain.size)
# 				if chain:  # FETCHED BIGGER VALID CHAIN (INCLUDING UTXOs)
# 					log.debug('[BLOCKCHAIN] Fetched bigger valid chain.')
#
# 					# -- FIND DIFFERENT BLOCKS --
# 					diff = Chain.Blockchain.find_block_diff(
# 						old_blocks=my_node.blockchain.blocks,
# 						new_blocks=chain.blocks
# 					)
#
# 					# Remove OLD UTXOs
# 					for indx in diff:
# 						# -- REMOVE OLD MY_UTXOS --
# 						tmp_block: Chain.Block = my_node.blockchain.blocks[indx]
# 						old_utxos = tmp_block.find_UTXOs(my_node.identity)
# 						my_node.my_UTXOs.difference_update(old_utxos)
#
# 					if len(diff) == 0:  # Just in case the Client has no block knowledge
# 						diff.append(0)
#
# 					# Add new UTXOs
# 					for indx in range(diff[0], len(chain.blocks)):
# 						tmp_block: Chain.Block = chain.blocks[indx]
# 						new_utxos = tmp_block.find_UTXOs(my_node.identity)
# 						my_node.my_UTXOs = my_node.my_UTXOs.union(new_utxos)
# 					# ---------------------
#
# 					my_node.blockchain = chain
# 					my_node.my_UTXOs.intersection_update(my_node.blockchain.UTXOs)  # Should solve above issue? TODO
# 					for my_utxo in my_node.my_UTXOs:
# 						my_utxo.get_balance(blockchain=my_node.blockchain)
# 			else:
# 				log.error('WTF')
# 	return json.dumps({
# 		'message': 'ok',
# 	})


@app.route(API_BROADCASTS_NEW_TRANSACTION, methods=['POST'])
@requires_auth()
def broadcasts_new_transaction():
	"""
	:return:
	"""
	from Uncuffed import my_node

	json_data = request.get_json()
	if not json_data:
		return json.dumps({
			'message': 'Incorrect JSON Data.'
		}), 400

	data = json.loads(json_data)
	transaction = Transactions.Transaction.from_json(data)

	if transaction.hash in my_node.processed_hashes:
		return json.dumps({
			'message': 'Already processed',
		})
	else:
		my_node.processed_hashes.append(transaction.hash)

	if isinstance(my_node, Nodes.Miner):
		success = my_node.add_transaction(transaction)
		if success:
			log.debug(f'[TRANSACTION - {transaction.hash}] Validated')
			n_handler.broadcast_transaction(transaction)
		else:
			log.debug(f'[TRANSACTION - {transaction.hash}] Rejected (INVALID or EXISTS)')
	elif isinstance(my_node, Nodes.Client):
		log.debug(f'[TRANSACTION - {transaction.hash}] ECHOING')
		n_handler.broadcast_transaction(transaction)

	return json.dumps({
		'message': 'ok',
	})
