from Crypto.PublicKey.RSA import RsaKey

import Uncuffed.helpers.logger

from flask import Flask
from typing import TYPE_CHECKING, Optional
from .helpers.paths import PATH_UPLOADS

if TYPE_CHECKING:
    from Uncuffed.nodes import ANode

# Create a custom logger
log = Uncuffed.helpers.logger.log

# Node
my_node: Optional['ANode'] = None

# Web App
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = PATH_UPLOADS


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg'}


def rsa_long_encrypt(pub_key: bytes, msg: bytes, length=100) -> bytes:
    "https://titanwolf.org/Network/Articles/Article?AID=7211ded3-94dd-499d-b38b-0974435061ba#gsc.tab=0"
    from Crypto.PublicKey import RSA
    from Crypto.Cipher import PKCS1_v1_5

    pubobj = RSA.importKey(pub_key)
    pubobj = PKCS1_v1_5.new(pubobj)
    res = []
    for i in range(0, len(msg), length):
        res.append(pubobj.encrypt(msg[i:i + length]))
    return b''.join(res)


def rsa_long_decrypt(priv_key: RsaKey, msg: bytes, length=128) -> bytes:
    "" " 128 for 1024bit certificates and 256 bits for 2048bit certificates" ""
    from Crypto.PublicKey import RSA
    from Crypto.Cipher import PKCS1_v1_5

    # privobj = RSA.importKey(priv_key)
    privobj = PKCS1_v1_5.new(priv_key)
    res = []
    for i in range(0, len(msg), length):
        res.append(privobj.decrypt(msg[i:i + length], b'xyz'))
    return b''.join(res)


@app.template_filter()
def pretty_date(time):
    from datetime import datetime
    now = datetime.now()
    if type(time) is int:
        diff = now - datetime.fromtimestamp(time)
    elif type(time) is float:
        diff = now - datetime.fromtimestamp(time)
    elif isinstance(time, datetime):
        diff = now - time
    elif not time:
        diff = now - now
    else:
        raise ValueError('invalid date %s of type %s' % (time, type(time)))
    second_diff = diff.seconds
    day_diff = diff.days
    if day_diff < 0:
        return ''

    if day_diff == 0:
        if second_diff < 10:
            return "just now"
        if second_diff < 60:
            return str(second_diff) + " seconds ago"
        if second_diff < 120:
            return "a minute ago"
        if second_diff < 3600:
            return str(round(second_diff / 60)) + " minutes ago"
        if second_diff < 7200:
            return "an hour ago"
        if second_diff < 86400:
            return str(round(second_diff / 3600)) + " hours ago"
    if day_diff == 1:
        return "Yesterday"
    if day_diff < 7:
        return str(day_diff) + " days ago"
    if day_diff < 31:
        return str(day_diff / 7) + " weeks ago"
    if day_diff < 365:
        return str(day_diff / 30) + " months ago"
    return str(day_diff / 365) + " years ago"


@app.template_filter()
def filter_sorted(value, reverse=False):
    return sorted(value, reverse=reverse)
