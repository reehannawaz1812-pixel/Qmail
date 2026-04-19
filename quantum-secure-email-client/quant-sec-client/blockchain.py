import hashlib
import json
from time import time

class Blockchain:
    def __init__(self):
        self.chain = []
        # Create the genesis block
        self.new_block(previous_hash='1', proof=100)

    def new_block(self, proof, previous_hash=None, data=None):
        """
        Create a new Block in the Blockchain
        :param proof: <int> The proof given by the Proof of Work algorithm
        :param previous_hash: (Optional) <str> Hash of previous Block
        :param data: (Optional) <dict> Transaction data (sender, receiver, level)
        :return: <dict> New Block
        """
        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'data': data or {},
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1]),
        }
        self.chain.append(block)
        return block

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

    def add_transaction(self, sender, receiver, level, status):
        """
        Adds a new transaction to the next block
        """
        data = {
            'sender': sender,
            'receiver': receiver,
            'security_level': level,
            'status': status,
            'quantum_signature': hashlib.sha256(f"{sender}{receiver}{time()}".encode()).hexdigest()[:16]
        }
        # For prototype, we mine immediately
        self.new_block(proof=12345, data=data)
        return self.hash(self.chain[-1])

    def get_chain(self):
        return self.chain
