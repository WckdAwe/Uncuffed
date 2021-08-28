import json

from Uncuffed import app, my_node
from ..routes import API_BLOCKCHAIN, API_BLOCKCHAIN_LENGTH, API_BLOCKCHAIN_BLOCKS


@app.route(API_BLOCKCHAIN, methods=['GET'])
def get_blockchain():
	"""
	:return: JSON representation of the whole blockchain.
	"""
	return my_node.blockchain.to_json()


@app.route(API_BLOCKCHAIN_LENGTH, methods=['GET'])
def get_blockchain_length():
	"""
	:return: JSON representation of the node's blockchain length.
	"""
	return json.dumps({
		'length': my_node.blockchain.size
	})


@app.route(API_BLOCKCHAIN_BLOCKS, methods=['GET'])
def get_blockchain_blocks():
	"""
	:return: JSON representation of the node's blocks.
	"""
	return json.dumps({
		'blocks': list(map(lambda o: o.to_dict(), my_node.blockchain.blocks)),
	})
