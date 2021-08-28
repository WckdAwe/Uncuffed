import json

from flask import request

from Uncuffed import app, my_node, log
from Uncuffed.network import NetworkHandler, Peer
from ..routes import API_NODES, API_NODES_INFO, API_NODES_LIST, API_NODES_REGISTER

n_handler: NetworkHandler = NetworkHandler.get_instance()

# @app.route('/api/broadcasts/new_block', methods=['POST'])
# def broadcasts_new_block():
# 	"""
# 	:return:
# 	"""
# 	json_data = request.get_json()
# 	if not json_data:
# 		return json.dumps({
# 			'message': 'Incorrect JSON Data.'
# 		}), 400
# 	data = json.loads(json_data)
# 	block = Blockchain.Block.from_json(data)
#
# 	if block.hash in my_node.processed_hashes:
# 		return json.dumps({
# 			'message': 'Already processed',
# 		})
# 	else:
# 		my_node.processed_hashes.append(block.hash)
#
# 	log.debug(f'[BLOCK - {block.hash}] Received')
# 	if isinstance(my_node, Nodes.Miner):
# 		if block.check_validity(
# 				prev_block=my_node.blockchain.last_block,
# 				lite=False,
# 				blockchain=my_node.blockchain
# 		):
# 			log.debug(f'[BLOCK - {block.hash}] Validated')
# 			my_node.blockchain.blocks.append(block)
#
# 			# -- UPDATE UTXO SET --
# 			my_node.blockchain.UTXOs.difference_update(block.extract_STXOs())
# 			my_node.blockchain.UTXOs = set(my_node.blockchain.UTXOs.union(block.extract_UTXOs()))
# 			# ---------------------
#
# 			# -- UPDATE MY UTXO SET --
# 			my_utxos = set(block.find_UTXOs(my_node.identity))
# 			my_node.my_UTXOs = my_node.my_UTXOs.union(my_utxos)
# 			my_node.my_UTXOs.intersection_update(my_node.blockchain.UTXOs)
# 			for my_utxo in my_node.my_UTXOs:  # This will fail, but will cache the value
# 				my_utxo.check_validity(sender=None, blockchain=my_node.blockchain)
# 			# ---------------------
#
# 			# -- REMOVE (NOW) INVALID TRANSACTIONS --
# 			for trans in block.verified_transactions:
# 				my_node.verified_transactions.pop(trans.hash, None)
# 			# ---------------------------------------
# 			my_node.network.broadcast_block(block)
# 		else:
# 			if block.index > my_node.blockchain.last_block.index + 1:
# 				log.debug(f'[BLOCK - {block.hash}] Rejected (AHEAD)')
# 				chain = my_node.network.check_peer_chains(my_node.blockchain.size)
# 				if chain:
# 					log.debug('[BLOCKCHAIN] Fetched bigger valid chain.')
# 					# -- UPDATE MY UTXO SET --
# 					diff = Blockchain.BlockChain.find_block_diff(
# 						old_blocks=my_node.blockchain.blocks,
# 						new_blocks=chain.blocks
# 					)
#
# 					# 2 Different for loops just in case a UTXO has just changed it's block
# 					# position.
#
# 					# Remove OLD UTXOs
# 					for indx in diff:
# 						tmp_block: Blockchain.Block = my_node.blockchain.blocks[indx]
# 						old_utxos = tmp_block.find_UTXOs(my_node.identity)
# 						my_node.my_UTXOs.difference_update(old_utxos)
#
# 						# -- COLLECT VALID TRANSACTIONS from our rejected block --
# 						for t_indx in range(1, len(tmp_block.verified_transactions)):
# 							trans = tmp_block.verified_transactions[t_indx]
# 							my_node.verified_transactions[trans.hash] = trans
#
# 					# Add new UTXOs
# 					for indx in range(diff[0], len(chain.blocks)):
# 						tmp_block: Blockchain.Block = chain.blocks[indx]
# 						new_utxos = tmp_block.find_UTXOs(my_node.identity)
# 						for n in new_utxos:
# 							log.error(f'Added UTXO: {n.hash}')
# 						my_node.my_UTXOs = my_node.my_UTXOs.union(new_utxos)
#
# 						# -- REMOVE TRANSACTIONS that are already in the block --
# 						for t_indx in range(1, len(tmp_block.verified_transactions)):
# 							trans = tmp_block.verified_transactions[t_indx]
# 							my_node.verified_transactions.pop(trans.hash, None)
# 					# ---------------------
#
# 					my_node.blockchain = chain
#
# 					my_node.my_UTXOs.intersection_update(my_node.blockchain.UTXOs)
# 					for my_utxo in my_node.my_UTXOs:  # This will fail, but will cache the value
# 						my_utxo.check_validity(sender=None, blockchain=my_node.blockchain)
# 			else:
# 				log.debug(f'[BLOCK - {block.hash}] Rejected (INVALID)')
# 	elif type(my_node) is Nodes.Client:
# 		log.debug(f'[BLOCK - {block.hash}] ECHOING')
# 		if block.check_validity(my_node.blockchain, lite=True):
# 			my_node.network.broadcast_block(block)  # Echo Transaction
#
# 	return json.dumps({
# 		'message': 'ok',
# 	})
#
#
# @app.route('/api/broadcasts/new_transaction', methods=['POST'])
# def broadcasts_new_transaction():
# 	"""
# 	:return:
# 	"""
# 	json_data = request.get_json()
# 	if not json_data:
# 		return json.dumps({
# 			'message': 'Incorrect JSON Data.'
# 		}), 400
# 	data = json.loads(json_data)
# 	transaction = Transactions.Transaction.from_json(data)
#
# 	if transaction.hash in my_node.processed_hashes:
# 		return json.dumps({
# 			'message': 'Already processed',
# 		})
# 	else:
# 		my_node.processed_hashes.append(transaction.hash)
#
# 	if isinstance(my_node, Nodes.Miner):
# 		success = my_node.add_transaction(transaction)
# 		if success:
# 			log.debug(f'[TRANSACTION - {transaction.hash}] Validated')
# 			my_node.network.broadcast_transaction(transaction)
# 		else:
# 			log.debug(f'[TRANSACTION - {transaction.hash}] Rejected (INVALID or EXISTS)')
# 	elif isinstance(my_node, Nodes.Client):
# 		log.debug(f'[TRANSACTION - {transaction.hash}] ECHOING')
# 		my_node.network.broadcast_transaction(transaction)
#
# 	return json.dumps({
# 		'message': 'ok',
# 	})