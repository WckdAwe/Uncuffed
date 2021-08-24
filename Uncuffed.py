import Uncuffed.chain as Chain
import Uncuffed.transactions as Transactions
import Uncuffed.messages as Messages
import Uncuffed.nodes as Nodes
import logging
logging.getLogger().setLevel(logging.DEBUG)

if __name__ == '__main__':

	key = Nodes.KeyFactory.load_key('WICKED')
	miner = Nodes.Miner(private_key=key)
	print('Miner priv\t\t: ', miner.private_key)
	print('Miner pub\t: ', miner.public_key)
	print('Miner ide\t: ', miner.identity)

	miner._construct_genesis_block()
	# miner.manual_mine()
	print(miner.blockchain)
	print(miner.blockchain.is_valid(
		lite=False
	))

	T_OUT = Transactions.TransactionOutput(
		recipient_address=miner.identity,
		value=42,
		message=Messages.TextMessage('Hello there...General Kenobi')
	)
	print(T_OUT)

	T_IN = Transactions.TransactionInput(
		block_index=0,
		transaction_index=0,
		output_index=0,
	)

	print('T_IN_valid:', T_IN.is_valid(
		sender=miner.identity,
		blockchain=miner.blockchain
	))

	T = Transactions.Transaction(
		sender=miner.identity,
		inputs=(T_IN, ),
		outputs=(T_OUT, ),
	)

	T.sign_transaction(miner.signer)

	print(
		T.is_valid(
			blockchain=miner.blockchain
		)
	)
	# block_0 = Chain.Block(
	# 	height=0,
	# 	transactions=(T, ),
	# 	previous_block_hash=None,
	# 	proof=None,
	# )
	#
	# print(block_0)
	#
	# blockchain = Chain.Blockchain(
	# 	blocks=[block_0],
	# )
	# print(blockchain)
	# blockchain.store_to_file()

	# blockchain = Chain.Blockchain.load_from_file()
	# print(blockchain)
