import threading

import Uncuffed.helpers.logger

from flask import Flask
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from Uncuffed.nodes import ANode

# Create a custom logger
log = Uncuffed.helpers.logger.log

# Web App
app = Flask(__name__)

# Node
my_node: Optional['ANode'] = None

