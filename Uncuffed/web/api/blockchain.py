import json

from Uncuffed import app
from ..routes import API_BLOCKCHAIN, API_BLOCKCHAIN_LENGTH, API_BLOCKCHAIN_BLOCKS
from ..decorators import requires_auth


@app.route(API_BLOCKCHAIN, methods=['GET'])
@requires_auth()
def get_blockchain():
	"""
	:return: JSON representation of the whole blockchain.
	"""
	from Uncuffed import my_node

	return my_node.blockchain.to_json()


@app.route(API_BLOCKCHAIN_LENGTH, methods=['GET'])
@requires_auth()
def get_blockchain_length():
	"""
	:return: JSON representation of the node's blockchain length.
	"""
	from Uncuffed import my_node

	return json.dumps({
		'length': my_node.blockchain.size
	})


@app.route(API_BLOCKCHAIN_BLOCKS, methods=['GET'])
@requires_auth()
def get_blockchain_blocks():
	"""
	:return: JSON representation of the node's blocks.
	"""
	from Uncuffed import my_node

	return json.dumps({
		'blocks': list(map(lambda o: o.to_dict(), my_node.blockchain.blocks)),
	})
