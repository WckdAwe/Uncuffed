from Crypto.PublicKey.RSA import RsaKey
from prettytable import PrettyTable

import UniCoin.Nodes as Nodes

import logging
log = logging.getLogger('werkzeug')


def menu_select_client_type(private_key, my_peer=None):
	print('-'*23, ' [UNICOIN - Select Client Type] ', '-'*23)
	print('1. Client')
	print('2. Miner')
	print('0. Exit')

	while True:
		inp = int(input('Selection: '))
		if inp not in range(0, 3):
			print('Incorrect input. Try again.')
			continue
		break

	if inp == 0:
		exit(0)
	elif inp == 1:
		return Nodes.Client(private_key, my_peer=my_peer)
	else:
		return Nodes.Miner(private_key, my_peer=my_peer)


def menu_generate_key() -> RsaKey:
	print('-'*23, ' [UNICOIN - Friendly name] ', '-'*23)
	print('Select a friendly name for your key.')
	print('Just try not to override any previous one and lose fortunes ^_^.')
	inp = str(input('Friendly name (Keep empty for random): '))
	key = Nodes.KeyFactory.create_key()
	Nodes.KeyFactory.store_key(key, inp)
	return key


def menu_select_key() -> RsaKey:
	import UniCoin.helpers as helpers
	import os

	try:
		path = helpers.paths.PATH_WALLETS
		addresses = [name.removesuffix('.der') for name in os.listdir(path) if os.path.isfile(os.path.join(path, name))]
	except Exception:
		addresses = []

	print('-'*23, ' [UNICOIN - Select address] ', '-'*23)
	print('1. Generate new address')
	for idx, address in enumerate(addresses):
		print(f'{idx+2}. {address}')
	print('0. Exit')

	while True:
		inp = int(input('Selection: '))
		if inp not in range(0, len(addresses)+2):
			print('Incorrect input. Try again.')
			continue
		break

	if inp == 0:
		exit(0)
	elif inp == 1:
		return menu_generate_key()
	else:
		return Nodes.KeyFactory.load_key(addresses[inp-2])


def menu_main(my_node: Nodes.Client):
	print('-'*23, f' [UNIWallet - {str(type(my_node).__name__).upper()}]', '-'*23)
	print('1. My Balance')
	print('2. Send Money')
	print('3. Dump Blockchain')
	print('4. Debug Console')
	if isinstance(my_node, Nodes.Miner):
		if my_node.is_mining:
			print('5. Stop Mining')
		else:
			print('5. Start Mining')

	print('0. Exit')

	while True:
		try:
			inp = int(input('Selection: '))
			if inp not in range(0, 6 if isinstance(my_node, Nodes.Miner) else 5):
				print('Incorrect input. Try again.')
				continue
			break
		except Exception:
			continue

	if inp == 0:
		exit(0)
	elif inp == 1:
		t = PrettyTable(['Transaction', 'Balance'])
		total = 0
		for utxo in my_node.my_UTXOs:
			t.add_row([utxo.hash, utxo.balance])
			if utxo.balance > 0:
				total += utxo.balance
		t.add_row(['Total: ', total])
		print(t)
	elif inp == 2:
		receivers = []
		print(f'Your available balance is: {my_node.balance}')
		while True:
			try:
				receiver = input('Send money to: ')
				value = int(input('Amount: '))
				resp = input(f'Are you sure you want to send {value} Unicoins to \'{receiver}\'? (Y/N): ')
				if resp.upper() == 'Y':
					receivers.append((receiver, value))

				more = input('Would you like to send more Unicoins? (Y/N): ')
				if more.upper() == 'Y':
					continue
				else:
					break
			except Exception:
				pass

		if len(receivers) > 0:
			print('You are about to send money to the following people: ')
			t = PrettyTable(['Address', 'Amount'])
			for address, amount in receivers:
				t.add_row([address, amount])
			print(t)
			resp = input('Execute? (Y/N): ')
			if resp.upper() == 'Y':
				if not my_node.send_coins(receivers):
					print('Failed to create transaction.')
				else:
					print('Unicoins sent!')
			else:
				print('Action cancelled!')
	elif inp == 3:
		print(my_node.blockchain)
	elif inp == 4:
		if log.level is not logging.DEBUG:
			log.setLevel(logging.DEBUG)
			input('Press any key to DISABLE Debug Console.\n')
			log.setLevel(logging.ERROR)
	elif inp == 5:
		my_node.toggle_mining()
		print(f'Miner has {"started" if my_node.is_mining else "stopped"} mining.')


