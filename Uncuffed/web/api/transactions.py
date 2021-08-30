import json
import Uncuffed.nodes as Nodes

from Uncuffed import app
from Uncuffed.network import NetworkHandler
from ..routes import API_TRANSACTIONS_PENDING, API_TRANSACTIONS_UTXO
from ..decorators import requires_auth

n_handler: NetworkHandler = NetworkHandler.get_instance()


@app.route(API_TRANSACTIONS_PENDING, methods=['GET'])
@requires_auth()
def get_pending_transactions():
    """
    :return: Returns all pending transactions to be added to a block of a specific node.
    """
    from Uncuffed import my_node

    if not isinstance(my_node, Nodes.Miner):
        return json.dumps({
            'message': 'Node is not a miner -> Node doesn\'t store transactions!'
        }), 404

    return json.dumps({
        'length': len(my_node.verified_transactions),
        'transactions': list(map(lambda o: o.to_dict(), my_node.verified_transactions))
    })


# TODO
@app.route(API_TRANSACTIONS_UTXO, methods=['GET'])
@requires_auth()
def my_utxo():
    """
    :return: A list of UTXOs that belong to this node
    """
    from Uncuffed import my_node

    if not isinstance(my_node, (Nodes.Miner, Nodes.Client)):
        return json.dumps({
            'message': 'Node must be a client or miner to have UTXO.'
        }), 404

    return json.dumps({
        'length': len(my_node.my_UTXOs),
        'total': sum([t.cached_balance for t in my_node.my_UTXOs]),
        'UTXOs':  list(map(lambda o: o.to_dict(), my_node.my_UTXOs)),
    })
