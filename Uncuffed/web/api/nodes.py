import json
import Uncuffed.network as Network

from flask import request

from Uncuffed import app, log
from ..routes import API_NODES, API_NODES_INFO, API_NODES_REGISTER
from ..decorators import requires_auth

n_handler: Network.NetworkHandler = Network.NetworkHandler.get_instance()


@app.route(API_NODES, methods=['GET'])
@requires_auth()
def get_nodes():
	"""
	:return: JSON representation of the node's peers.
	"""
	peers = n_handler.network.get_peers()
	return json.dumps({
		'length': len(peers),
		'nodes': [str(peer) for peer in n_handler.network.get_peers()]
	})


@app.route(API_NODES_INFO)
@requires_auth()
def get_node_information():
	"""
	:return: JSON representation of the node's information, like the node's type
	and public_key.
	"""
	from Uncuffed import my_node

	return json.dumps({
		'node_type': my_node.node_type,
		'public_key': str(my_node.identity)
	})


@app.route(API_NODES_REGISTER, methods=['POST'])
@requires_auth()
def receive_registration_request():
	"""
	Attempts to register a list of node addresses to the system.
	:return: JSON representation of which nodes where registered and which not.
	"""
	from Uncuffed import my_node

	json_data = request.get_json()
	if not json_data or not isinstance(json_data, list):
		return json.dumps({
			'message': 'Expected a json list of addresses.'
		}), 400

	registered = []
	not_registered = []
	for address in json_data:
		try:
			if not isinstance(address, str):
				continue

			peer = Network.Peer.from_string(address)

			if n_handler.network.register_peer(peer):
				registered.append(address)

				# Check if another peer has a bigger valid chain
				# If so, fetch it and make it your new chain!

				# TODO: This should be extracted to somewhere else, otherwise the node could be attacked.
				if n_handler.check_chain_length(peer) > my_node.blockchain.size:
					log.info(f'[PEER] \'{peer}\' has longer blockchain length.')
					chain = n_handler.steal_blockchain(peer)
					if chain.is_valid():
						my_node.blockchain = chain
						log.info(f'[PEER] Now using the blockchain of peer \'{peer}\'')
					else:
						log.info(f'[PEER] Failed to validate blockchain of peer \'{peer}\'.')
			else:
				not_registered.append(address)
		except Exception as e:
			not_registered.append(address)
			log.warn(f'receive_registration_request {e}')
			continue
	return json.dumps({
		'registered': registered,
		'not_registered': not_registered
	})
