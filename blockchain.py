# Author: Doan Bui (bxdoan93@gmail.com)
# https://github.com/bxdoan/start-block-chain

import falcon

api = application = falcon.API()


class Blockchain(object):
    def __init__(self):
        self.chain = []
        self.current_transactions = []

    def new_block(self):
        # Creates a new Block and adds it to the chain
        pass

    def new_transaction(self):
        # Adds a new transaction to the list of transactions
        pass

    @staticmethod
    def hash(block):
        # Hashes a Block
        pass

    @property
    def last_block(self):
        # Returns the last Block in the chain
        pass

    def on_get(self, req, resp):
        resp.status = falcon.HTTP_200


api.add_route('/', Blockchain())
