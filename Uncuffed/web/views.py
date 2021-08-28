import Uncuffed.nodes as Nodes


from flask import render_template, redirect, request, url_for
from Uncuffed import app


@app.route('/', methods=['GET', 'POST'])
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


@app.route('/chat/', methods=['GET', 'POST'])
def start_chat():
	if request.method == 'POST':
		return redirect(url_for('chat', address=request.form['chat_id']))
	else:
		return redirect(url_for('index'))


@app.route('/chat/<address>/', methods=['GET', 'POST'])
def chat(address: str):
	from Uncuffed import my_node

	return render_template(
		'chat.html',
		page_title='&bull; Chat',
		user=my_node,
		other=address,
	)
