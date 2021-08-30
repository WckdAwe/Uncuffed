import Uncuffed.nodes as Nodes
import Uncuffed.messages as Messages

from flask import render_template, redirect, request, url_for
from Uncuffed import app

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
		user=my_node
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
		my_node.send_message(
			address=address,
			message=Messages.TextMessage(
				message=request.form.get('text_message') or None
			),
			total_gas=int(request.form.get('blabber_gas')) or 0
		)

	return render_template(
		'chat.html',
		page_title='&bull; Chat',
		user=my_node,
		other=address,
	)
