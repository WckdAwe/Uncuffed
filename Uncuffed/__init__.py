import Uncuffed.helpers.logger

from flask import Flask
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from Uncuffed.nodes import ANode

# Create a custom logger
log = Uncuffed.helpers.logger.log

# Node
my_node: Optional['ANode'] = None

# Web App
app = Flask(__name__)
