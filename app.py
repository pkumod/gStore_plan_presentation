from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from gstore import GstoreConnector
from flask_cors import CORS
import json

gStore_config = {
    'ip': '115.27.161.37',
    'port': '9000',
    'user': 'root',
    'password': '123456',
    'database': 'lubm'
}
gc = GstoreConnector(gStore_config['ip'], gStore_config['port'], gStore_config['user'], gStore_config['password'])

app = Flask(__name__, static_url_path='', static_folder='./plan/dist/')
app.config['threaded'] = True
CORS(app)


@app.route('/')
def server():
    return app.send_static_file('index.html')


@app.route('/query_opt', methods=['POST'])
def query():
    req = request.get_json()
    query = req['query']
    plan = req['plan']
    res = gc.query_opt(db_name=gStore_config['database'], format='json', sparql=query, plan=plan)
    print('Received query: \n' + query)
    print('Received Plan: \n' + json.loads(res)['Plan'])
    return res


@app.route('/query', methods=['POST'])
def query_opt():
    req = request.get_json()
    query = req['query']
    plan = req['plan']
    print('Received Query: \n' + query)
    print('and custom Plan: \n' + plan)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
