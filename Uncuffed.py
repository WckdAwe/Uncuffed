import threading
import time

import Uncuffed as Unc
import Uncuffed.nodes as Nodes
import logging


# import Uncuffed.chain as Chain
# import Uncuffed.transactions as Transactions
# import Uncuffed.messages as Messages
# import Uncuffed.network as Network

logging.getLogger().setLevel(logging.DEBUG)


def tst_run(port=5000):
	import Uncuffed as Uncuffed
	Uncuffed.my_node = Nodes.Miner(Nodes.KeyFactory.create_key())

	import Uncuffed.web
	Uncuffed.app.run(port=port)


def run(port=5000):
	# key = menus.menu_select_key()
	# my_node = menus.menu_select_client_type(key, my_peer=Nodes.Peer("127.0.0.1", port))
	Unc.my_node = Nodes.Miner(Nodes.KeyFactory.create_key())

	# -- START WEB SERVER --
	print('Good to go... Starting web server...')
	import Uncuffed.web
	w = threading.Thread(target=Unc.app.run, args=(None, port,), daemon=True)
	w.start()
	# ----------------------

	time.sleep(1)
	while True:
		time.sleep(5)
# 	# -- START MENU --
# 	time.sleep(1)
# 	while True:
# 		menus.menu_main(my_node)
#


if __name__ == '__main__':
	tst_run(5000)
	# key = Nodes.KeyFactory.load_key('WICKED')
	# miner = Nodes.Miner(private_key=key)
	# print('Miner priv\t\t: ', miner.private_key)
	# print('Miner pub\t: ', miner.public_key)
	# print('Miner ide\t: ', miner.identity)
	#
	# miner._construct_genesis_block()
	# print(miner.blockchain)
	# print(miner.blockchain.is_valid(
	# 	lite=False
	# ))
	#
	# T_OUT = Transactions.TransactionOutput(
	# 	recipient_address=miner.identity,
	# 	value=42,
	# 	message=Messages.TextMessage('Hello there...General Kenobi')
	# )
	# print(T_OUT)
	#
	# T_IN = Transactions.TransactionInput(
	# 	block_index=0,
	# 	transaction_index=0,
	# 	output_index=0,
	# )
	#
	# print('T_IN_valid:', T_IN.is_valid(
	# 	sender=miner.identity,
	# 	blockchain=miner.blockchain
	# ))
	#
	# T = Transactions.Transaction(
	# 	sender=miner.identity,
	# 	inputs=(T_IN, ),
	# 	outputs=(T_OUT, ),
	# )
	#
	# T.sign_transaction(miner.signer)
	#
	# print(
	# 	T.is_valid(
	# 		blockchain=miner.blockchain
	# 	)
	# )
	#
	# miner.add_transaction(T)
	# miner.manual_mine()
	# print(miner.blockchain)
	# print(miner.blockchain.is_valid(
	# 	lite=False
	# ))

