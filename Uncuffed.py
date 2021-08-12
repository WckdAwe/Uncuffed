import Uncuffed.chain as Chain
import Uncuffed.transactions as Transactions
import Uncuffed.messages as Messages
import Uncuffed.nodes as Nodes

if __name__ == '__main__':
	# key = Nodes.KeyFactory.load_key('WICKED')
	# print(key)
	#
	# client = Nodes.Client(private_key=key)
	# print('Client priv\t\t: ', client.private_key)
	# print('Client pub\t: ', client.public_key)
	#
	# T_OUT = Transactions.TransactionOutput(
	# 	recipient_address='DemoUser',
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
	# print(T_IN)
	#
	# T = Transactions.Transaction(
	# 	sender=client.identity,
	# 	inputs=(T_IN, ),
	# 	outputs=(T_OUT, ),
	# )
	#
	# T.sign_transaction(client.signer)
	# print(T)
	# print(T.verify_signature())
	#
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

	blockchain = Chain.Blockchain.load_from_file()
	print(blockchain)
