# Author: Doan Bui (bxdoan93@gmail.com)
# https://github.com/bxdoan/start-blockchain
from time import time
from uuid import uuid4
from urllib.parse import urlparse

import falcon
import hashlib
import json
import requests

api = application = falcon.API()

# Generate a globally unique address for this node
node_identifier = str(uuid4()).replace('-', '')

class Blockchain(object):
    def __init__(self):
        self.chain = []
        self.current_transactions = []
        self.nodes = set()

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
            'index'         : len(self.chain) + 1,
            'timestamp'     : time(),
            'transactions'  : self.current_transactions,
            'proof'         : proof,
            'previous_hash' : previous_hash or self.hash(self.chain[-1]),
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

    def register_node(self, address):
        """
        Add a new node to the list of nodes
        :param address: <str> Address of node. Eg. 'http://localhost:5555'
        :return: None
        """
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)

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

    def valid_chain(self, chain):
        """
        Determine if a given blockchain is valid
        :param chain: <list> A blockchain
        :return: <bool> True if valid, False if not
        """

        last_block = chain[0]
        current_index = 1

        while current_index < len(chain):
            block = chain[current_index]
            print(f'{last_block}')
            print(f'{block}')
            print("\n-----------\n")
            # Check that the hash of the block is correct
            if block['previous_hash'] != self.hash(last_block):
                return False

            # Check that the Proof of Work is correct
            if not self.valid_proof(last_block['proof'], block['proof']):
                return False

            last_block = block
            current_index += 1

        return True

    def resolve_conflicts(self):
        """
        This is our Consensus Algorithm, it resolves conflicts
        by replacing our chain with the longest one in the network.
        :return: <bool> True if our chain was replaced, False if not
        """

        neighbours = self.nodes
        new_chain = None

        # We're only looking for chains longer than ours
        max_length = len(self.chain)

        # Grab and verify the chains from all the nodes in our network
        for node in neighbours:
            response = requests.get(f'http://{node}/chain')

            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']

                # Check if the length is longer and the chain is valid
                if length > max_length and self.valid_chain(chain):
                    max_length = length
                    new_chain = chain

        # Replace our chain if we discovered a new, valid chain longer than ours
        if new_chain:
            self.chain = new_chain
            return True

        return False

    def on_get(self, req, resp):
        response = {
            'message' : 'together with Doan learning blockchain'
        }

        resp.status = falcon.HTTP_200
        resp.body = json.dumps(response)


# Instantiate the Blockchain
blockchain = Blockchain()

# RESOURCE API
class ResourcesAllChain:
    def on_get(self, req, resp):
        response = {
            'chain' : blockchain.chain,
            'length': len(blockchain.chain),
        }

        resp.status = falcon.HTTP_200
        resp.body = json.dumps(response)


class ResourcesTransactionNew:
    def on_post(self, req, resp):
        body = req.media
        required = ['sender', 'recipient', 'amount']
        if not all(k in body for k in required):
            raise falcon.HTTPBadRequest('Wrong request body',
                                        'A valid JSON document is required.')

        index = blockchain.new_transaction(body['sender'], body['recipient'], body['amount'])
        response = {'message': f'Transaction will be added to Block {index}'}

        resp.status = falcon.HTTP_200
        resp.body = json.dumps(response)

class ResourcesMine:
    def on_get(self, req, resp):
        """
         It has to do three things:
        * Calculate the Proof of Work
        * Reward the miner (us) by adding a transaction granting us 1 coin
        * Forge the new Block by adding it to the chain
        """
        # We run the proof of work algorithm to get the next proof...
        last_block = blockchain.last_block
        last_proof = last_block['proof']
        proof      = blockchain.proof_of_work(last_proof)

        # We must receive a reward for finding the proof.
        # The sender is "0" to signify that this node has mined a new coin.
        blockchain.new_transaction(
            sender    = "0",
            recipient = node_identifier,
            amount    = 1,
        )

        # Forge the new Block by adding it to the chain
        previous_hash = blockchain.hash(last_block)
        block = blockchain.new_block(proof, previous_hash)

        response = {
            'message'      : "New Block Forged",
            'index'        : block['index'],
            'transactions' : block['transactions'],
            'proof'        : block['proof'],
            'previous_hash': block['previous_hash'],
        }

        resp.status = falcon.HTTP_200
        resp.body = json.dumps(response)

class ResourcesNodes:
    def on_get(self, req, resp):
        replaced = blockchain.resolve_conflicts()

        if replaced:
            response = {
                'message'  : 'Our chain was replaced',
                'new_chain': blockchain.chain
            }
        else:
            response = {
                'message': 'Our chain is authoritative',
                'chain'  : blockchain.chain
            }

        resp.status = falcon.HTTP_200
        resp.body = json.dumps(response)

    def on_post(self, req, resp):
        values = req.media

        nodes = values['nodes']
        if nodes is None:
            falcon.HTTPBadRequest('Wrong request body',
                                  'A valid JSON document is required.')

        for node in nodes:
            blockchain.register_node(node)

        response = {
            'message'    : 'New nodes have been added',
            'total_nodes': list(blockchain.nodes),
        }

        resp.status = falcon.HTTP_200
        resp.body = json.dumps(response)


# ROUTE API
api.add_route('/', Blockchain())
api.add_route('/mine', ResourcesMine())
api.add_route('/transactions/new', ResourcesTransactionNew())
api.add_route('/chain', ResourcesAllChain())
api.add_route('/nodes/register', ResourcesNodes())
api.add_route('/nodes/resolve', ResourcesNodes())
