import flask
import Uncuffed as Unc

from functools import wraps
from flask import redirect, url_for


def requires_auth():
    def wrapper(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if Unc.my_node is None:
                return redirect(url_for('selector'))
            else:
                return f(*args, **kwargs)
        return decorated
    return wrapper


def requires_unauth():
    def wrapper(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if Unc.my_node is not None:
                return redirect(url_for('index'))
            else:
                return f(*args, **kwargs)
        return decorated
    return wrapper
