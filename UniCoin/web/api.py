import json
import UniCoin.Nodes as Nodes
import UniCoin.Transactions as Transactions
import UniCoin.Blockchain as Blockchain

from flask import request
from UniCoin import app, my_node

import logging
log = logging.getLogger('werkzeug')
