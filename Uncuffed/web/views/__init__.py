import base64
from typing import Optional

import Uncuffed.nodes as Nodes
import Uncuffed.messages as Messages

from flask import render_template, redirect, request, url_for
from Uncuffed import app
from Uncuffed.chats.Chat import Chat, get_all_chats
from ..decorators import requires_auth, requires_unauth


@app.route('/', methods=['GET', 'POST'])
@requires_auth()
def index():
	from Uncuffed import my_node

	if request.method == 'POST' and request.form['toggle_mining']:
		if isinstance(my_node, Nodes.Miner):
			my_node.toggle_mining()

	return render_template(
		'index.html',
		page_title='&bull; Home',
		user=my_node,
		chats=get_all_chats().values()
	)


@app.route('/selector', methods=['GET', 'POST'])
@requires_unauth()
def selector():
	import Uncuffed
	import Uncuffed.nodes as Nodes
	if request.method == 'POST':
		node_type = request.form.get('node_type') or 'node_miner'

		if node_type == 'node_client':
			Uncuffed.my_node = Nodes.Client(Nodes.KeyFactory.load_or_generate_key())
		else:
			Uncuffed.my_node = Nodes.Miner(Nodes.KeyFactory.load_or_generate_key())

		return redirect(url_for('index'))

	return render_template(
		'selector.html',
		page_title='&bull; Selector',
	)


@app.route('/chat/', methods=['GET', 'POST'])
@requires_auth()
def start_chat():
	if request.method == 'POST':
		return redirect(url_for('chat', address=request.form['chat_id']))
	else:
		return redirect(url_for('index'))


@app.route('/chat/<address>/', methods=['GET', 'POST'])
@requires_auth()
def chat(address: str):
	from Uncuffed import my_node
	import Uncuffed.nodes as Nodes

	if not isinstance(my_node, Nodes.Client):
		return redirect(url_for('index'))

	if request.method == 'POST':
		# -1: FUND TRANSFER, 0: PLAIN, 1: ENCRYPTED
		msg_type = int(request.form.get('msg_type'))
		file_img = request.files['file_img']
		text_message = request.form.get('text_message')
		message: Optional[Messages.AMessage] = None

		if file_img.filename == '' and text_message == '' and msg_type != -1:
			pass
		elif file_img.filename != '':
			if msg_type == 0:
				message = Messages.ImageMessage.from_file(file=file_img)
			elif msg_type == 1:
				message = Messages.EncryptedImageMessage.from_file(file=file_img)
		elif text_message != '':
			if msg_type == 0:
				message = Messages.PlainTextMessage(
					message=request.form.get('text_message') or ''
				)
			elif msg_type == 1:
				message = Messages.EncryptedTextMessage(
					message=request.form.get('text_message') or ''
				)
		elif msg_type == -1:
			pass
		if message:
			my_node.send_message(
				address=address,
				message=message,
				total_gas=int(request.form.get('blabber_gas')) or 0
			)

	# Bad way..
	chats = get_all_chats()
	my_chat = None

	if address in chats.keys():
		my_chat = chats[address]
	else:
		my_chat = Chat.load_from_file(
			friendly_name=address,
		)

	return render_template(
		'chat.html',
		page_title='&bull; Chat',
		user=my_node,
		other=address,
		chat=my_chat
	)
