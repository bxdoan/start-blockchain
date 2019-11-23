# Author: Doan Bui (bxdoan93@gmail.com)
# https://github.com/bxdoan/start-blockchain
from time import time
from uuid import uuid4

import falcon
import hashlib
import json

api = application = falcon.API()

# Generate a globally unique address for this node
node_identifier = str(uuid4()).replace('-', '')

class Blockchain(object):
    def __init__(self):
        self.chain = []
        self.current_transactions = []

        # Create the genesis block
        self.new_block(proof=100, previous_hash=1)

    def new_block(self, proof, previous_hash=None):
        """
        Create a new Block in the Blockchain
        :param proof: <int> The proof given by the Proof of Work algorithm
        :param previous_hash: (Optional) <str> Hash of previous Block
        :return: <dict> New Block
        """

        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'transactions': self.current_transactions,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1]),
        }

        # Reset the current list of transactions
        self.current_transactions = []

        self.chain.append(block)
        return block

    def new_transaction(self, sender, recipient, amount):
        """
        Creates a new transaction to go into the next mined Block
        :param sender: <str> Address of the Sender
        :param recipient: <str> Address of the Recipient
        :param amount: <int> Amount
        :return: <int> The index of the Block that will hold this transaction
        """
        self.current_transactions.append({
            'sender': sender,
            'recipient': recipient,
            'amount': amount,
        })

        return self.last_block['index'] + 1

    @property
    def last_block(self):
        return self.chain[-1]

    @staticmethod
    def hash(block):
        """
        Creates a SHA-256 hash of a Block
        :param block: <dict> Block
        :return: <str>
        """

        # We must make sure that the Dictionary is Ordered, or we'll have inconsistent hashes
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    def proof_of_work(self, last_proof):
        """
        Simple Proof of Work Algorithm:
         - Find a number p' such that hash(pp') contains leading 4 zeroes, where p is the previous p'
         - p is the previous proof, and p' is the new proof
        :param last_proof: <int>
        :return: <int>
        """

        proof = 0
        while self.valid_proof(last_proof, proof) is False:
            proof += 1

        return proof

    @staticmethod
    def valid_proof(last_proof, proof):
        """
        Validates the Proof: Does hash(last_proof, proof) contain 4 leading zeroes?
        :param last_proof: <int> Previous Proof
        :param proof: <int> Current Proof
        :return: <bool> True if correct, False if not.
        """

        guess = f'{last_proof}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"

    def on_get(self, req, resp):
        response = {
            'chain' : self.chain,
            'length': len(self.chain),
        }

        resp.status = falcon.HTTP_200
        resp.body = json.dumps(response)

class ResourcesTransactionNew(Blockchain):
    def on_post(self, req, resp):
        body = req.media
        required = ['sender', 'recipient', 'amount']
        if not all(k in body for k in required):
            raise falcon.HTTPBadRequest('Wrong request body',
                                        'A valid JSON document is required.')
        index = Blockchain.new_transaction(self, body['sender'], body['recipient'], body['amount'])
        response = {'message': f'Transaction will be added to Block {index}'}

        resp.status = falcon.HTTP_200
        resp.body = json.dumps(response)

class ResourcesMine(Blockchain):
    def on_get(self, req, resp):
        """
         It has to do three things:
        * Calculate the Proof of Work
        * Reward the miner (us) by adding a transaction granting us 1 coin
        * Forge the new Block by adding it to the chain
        """
        # We run the proof of work algorithm to get the next proof...
        last_block = self.last_block
        last_proof = last_block['proof']
        proof = self.proof_of_work(last_proof)

        # We must receive a reward for finding the proof.
        # The sender is "0" to signify that this node has mined a new coin.
        self.new_transaction(
            sender="0",
            recipient=node_identifier,
            amount=1,
        )

        # Forge the new Block by adding it to the chain
        previous_hash = self.hash(last_block)
        block = self.new_block(proof, previous_hash)

        response = {
            'message'      : "New Block Forged",
            'index'        : block['index'],
            'transactions' : block['transactions'],
            'proof'        : block['proof'],
            'previous_hash': block['previous_hash'],
        }

        resp.status = falcon.HTTP_200
        resp.body = json.dumps(response)


api.add_route('/mine', ResourcesMine())
api.add_route('/transactions/new', ResourcesTransactionNew())
api.add_route('/chain', Blockchain())