import hashlib
import json
from time import time
from uuid import uuid4

from flask import Flask, jsonify, request, render_template


class Blockchain(object):
    def __init__(self):
        self.chain = []
        self.current_transactions = []

        # Create the genesis block
        self.new_block(previous_hash=1, proof=100)

        self.score = {}

    def new_transaction(self, sender, recipient, amount):
        self.current_transactions.append({
            'sender': sender.strip(),
            'recipient': recipient.strip(),
            'amount': amount})

        return self.last_block['index'] + 1



    def new_block(self, proof, previous_hash=None):
        """
        Create a new Block in the Blockchain

        A block should have:
        * Index
        * Timestamp
        * List of current transactions
        * The proof used to mine this block
        * The hash of the previous block

        :param proof: <int> The proof given by the Proof of Work algorithm
        :param previous_hash: (Optional) <str> Hash of previous Block
        :return: <dict> New Block
        """

        block = {
            'index': len(self.chain)+1,
            'timestamp': time(),
            'transactions': self.current_transactions,
            'proof': proof,
            'prev_block': previous_hash or self.hash(self.last_block)
        }

        # reset list of transaction
        self.current_transactions = []
        # append the chain to the block
        self.chain.append(block)
        return block


    def hash(self, block):
        """
        Creates a SHA-256 hash of a Block

        :param block": <dict> Block
        "return": <str>
        """

        encoding = json.dumps(block, sort_keys=True).encode()
        _hash = hashlib.sha256(encoding).hexdigest()
        return _hash

        # Use json.dumps to convert json into a string
        # Use hashlib.sha256 to create a hash
        # It requires a `bytes-like` object, which is what
        # .encode() does.
        # It converts the Python string into a byte string.
        # We must make sure that the Dictionary is Ordered,
        # or we'll have inconsistent hashes

        # TODO: Create the block_string

        # TODO: Hash this string using sha256

        # By itself, the sha256 function returns the hash in a raw string
        # that will likely include escaped characters.
        # This can be hard to read, but .hexdigest() converts the
        # hash to a string of hexadecimal characters, which is
        # easier to work with and understand

        # TODO: Return the hashed block string in hexadecimal format
        pass


    @property
    def last_block(self):
        return self.chain[-1]


        # return proof

    @staticmethod
    def valid_proof(block_string, proof):
        """
        Validates the Proof:  Does hash(block_string, proof) contain 3
        leading zeroes?  Return true if the proof is valid
        :param block_string: <string> The stringified block to use to
        check in combination with `proof`
        :param proof: <int?> The value that when combined with the
        stringified previous block results in a hash that has the
        correct number of leading zeroes.
        :return: True if the resulting hash is a valid proof, False otherwise
        """
        guess = f'{block_string}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()

        # 6 leading?
        return guess_hash[:6] == "0"*6

    def last_block_string(self):
        block = self.last_block
        last_block_string = json.dumps(block, sort_keys=True)
        return last_block_string



# Instantiate our Node
app = Flask(__name__)
import os
app.static_folder = os.path.abspath('static')

# Generate a globally unique address for this node
node_identifier = str(uuid4()).replace('-', '')

# Instantiate the Blockchain
blockchain = Blockchain()


@app.route('/transaction/new', methods=['POST'])
def transaction_new():
    data = request.get_json()
    required = ['sender', 'recipient', 'amount']
    if not all(k in values for k in required):
        response = {'message': 'Missing values'}
        return jsonify(response), 400

    index = blockchain.new_transaction(data['sender'],
                                       data['recipient'],
                                       data['amount'])

    response = {'message': f'Transaction will be added to block {index}'}
    return jsonify(response), 201



@app.route('/mine', methods=['POST'])
def mine():
    # Run the proof of work algorithm to get the next proof

    data = request.get_json()
    _id = data['id']
    proof = data['proof']
    last_block_string = blockchain.last_block_string()

    response = {'msg' : 'Sorry brother'}

    try:
        if blockchain.valid_proof(last_block_string, proof):
            # Forge the new Block by adding it to the chain with the proof
            previous_hash = blockchain.hash(blockchain.last_block)
            block = blockchain.new_block(proof, previous_hash)

            blockchain.new_transaction('0', _id, 1) # give them gold

            response = {
                'new_block': block,
                'msg': 'New block forged'
            }

            return jsonify(response), 200
        else:
            return jsonify(response), 500

    except Exception as e:
        print('---------')
        print(e)
        print( response )
        print('+++++++++')

    return jsonify(response), 200

@app.route('/last_block', methods=['GET'])
def last_block():
    return jsonify(blockchain.last_block), 200


@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain)
        # TODO: Return the chain and its current length
    }
    return jsonify(response), 200

@app.route('/account_info', methods=['POST'])
def account_info():
    data = request.get_json()
    _id = data['id']
    if _id is None:
        return jsonify(), 200

    try:
        amount = 0
        transactions = []

        def _transaction(t):
            nonlocal amount
            nonlocal transactions
            if t['sender'] == _id:
                amount -= t['amount']
            if t['recipient'] == _id:
                amount += t['amount']
            transactions.append(t)

        for block in blockchain.chain:
            t_s = block['transactions']
            for t in t_s:
                _transaction(t)

        for t in blockchain.current_transactions:
            _transaction(t)

        response = {'coins': amount,
                    'transactions': transactions}
        return jsonify(response), 200

    except Exception as e:
        print(e)
        return jsonify({'msg':f'Error {e}'}), 500



@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


# Run the program on port 5000
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
