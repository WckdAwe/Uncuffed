import json

from flask import request

from Uncuffed import app, my_node, log
from Uncuffed.network import NetworkHandler, Peer
from ..routes import API_NODES, API_NODES_INFO, API_NODES_LIST, API_NODES_REGISTER

n_handler: NetworkHandler = NetworkHandler.get_instance()


@app.route(API_NODES, methods=['GET'])
def get_nodes():
	"""
	:return: JSON representation of the node's peers.
	"""
	return json.dumps({
		'length': 0,
		'nodes': [str(peer) for peer in n_handler.network.get_peers()]
	})


@app.route(API_NODES_INFO)
def get_node_information():
	"""
	:return: JSON representation of the node's information, like the node's type
	and public_key.
	"""
	return json.dumps({
		'node_type': my_node.node_type,
		'public_key': str(my_node.identity)
	})


@app.route(API_NODES_REGISTER, methods=['POST'])
def receive_registration_request():
	"""
	Attempts to register a list of node addresses to the system.
	:return: JSON representation of which nodes where registered and which not.
	"""
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

			peer = Peer.from_string(address)

			if n_handler.network.register_peer(peer):
				registered.append(address)

				# TODO: This should be extracted to somewhere else, otherwise the node could be attacked.
				if n_handler.check_chain_length(peer) > my_node.blockchain.size:
					log.debug(f'[PEER] \'{peer}\' has longer blockchain length.')
					chain = n_handler.steal_blockchain(peer)
					if chain.is_valid():
						my_node.blockchain = chain
						log.debug(f'[PEER] Now using the blockchain of peer \'{peer}\'')
					else:
						log.debug(f'[PEER] Failed to validate blockchain of peer \'{peer}\'.')
			else:
				not_registered.append(address)
		except Exception as e:
			not_registered.append(address)
			log.warn(e)
			continue
	return json.dumps({
		'registered': registered,
		'not_registered': not_registered
	})
