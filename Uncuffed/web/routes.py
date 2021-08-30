# ------ [ API ] ------
API = '/api'

# ---------- [ BLOCKCHAIN ] ----------
API_BLOCKCHAIN = f'{API}/blockchain'
API_BLOCKCHAIN_LENGTH = f'{API_BLOCKCHAIN}/length'
API_BLOCKCHAIN_BLOCKS = f'{API_BLOCKCHAIN}/blocks'


# ---------- [ BROADCASTS ] ----------
API_BROADCASTS = f'{API}/broadcasts'
API_BROADCASTS_NEW_BLOCK = f'{API_BROADCASTS}/new_block'
API_BROADCASTS_NEW_TRANSACTION = f'{API_BROADCASTS}/new_transaction'


# ---------- [ TRANSACTIONS ] ----------
API_TRANSACTIONS = f'{API}/transactions'
API_TRANSACTIONS_PENDING = f'{API_TRANSACTIONS}/pending'
API_TRANSACTIONS_UTXO = f'{API_TRANSACTIONS}/UTXO'


# ---------- [ NODES ] ----------
API_NODES = f'{API}/nodes'
API_NODES_LIST = f'{API_NODES}/list'
API_NODES_INFO = f'{API_NODES}/info'
API_NODES_REGISTER = f'{API_NODES}/register'


# ------ [ WEB ] ------
WEB_HOME = '/'
WEB_SELECTOR = '/selector'
WEB_CHAT = '/chat'
WEB_CHAT_WITH_ADDRESS = f'{WEB_CHAT}/<address>'
