from functools import reduce
import json


from utility.hash_util import hash_block
from utility.verification import Verification

from block import Block
from transaction import Transaction
from wallet import Wallet

MINING_REWARD = 10.0


class Blockchain:
    
    def __init__(self, hosting_node_id):
        print('Initializing blockchain')
        genesis_block = Block(0, '', [], 100, 0)
        self.chain = [genesis_block]
        self.__open_transactions = []
        self.load_data()
        self.hosting_node = hosting_node_id


    # In the code of this class we continue using self.__chain because if we append to the property
    # we are really appending to a copy of the chain.... BEWARE!!!
    @property
    def chain(self):
        return self.__chain[:]

    @chain.setter
    def chain(self, val):
        self.__chain = val

    def get_open_transactions(self):
        return self.__open_transactions[:]

    def load_data(self):
        try:
            with open('blockchain.txt', mode='r') as f:
                file_content = f.readlines()

                blockchain = json.loads(file_content[0][:-1])
                updated_blockchain = []
                for block in blockchain:
                    converted_tx = [Transaction(tx['sender'], tx['recipient'], tx['signature'], tx['amount']) for tx in
                                    block['transactions']]
                    updated_block = Block(block['index'], block['previous_hash'], converted_tx, block['proof'],
                                          block['timestamp'])
                    updated_blockchain.append(updated_block)
                self.chain = updated_blockchain

                open_transactions = json.loads(file_content[1])
                updated_transactions = []
                for tx in open_transactions:
                    updated_tx = Transaction(tx['sender'], tx['recipient'], tx['signature'], tx['amount'])
                    updated_transactions.append(updated_tx)
                self.__open_transactions = updated_transactions
        except (IOError, IndexError):
            print('File not found!!!')

    def save_data(self):
        try:
            with open('blockchain.txt', mode='w') as f:
                saveable_chain = [block.__dict__ for block in
                                  [Block(block_el.index, block_el.previous_hash,
                                         [tx.__dict__ for tx in block_el.transactions],
                                         block_el.proof, block_el.timestamp) for block_el in self.__chain]]

                f.write(json.dumps(saveable_chain))
                f.write('\n')
                saveable_tx = [tx.__dict__ for tx in self.__open_transactions]
                f.write(json.dumps(saveable_tx))
        except IOError:
            print('Saving failed')

    def proof_of_work(self):
        """
        Tries sequential numbers until it finds one that solves the Proof of Work challenge
        :return: An integer which is the number that solves the Proof of Work challenge.
        """
        last_block = self.__chain[-1]
        last_hash = hash_block(last_block)
        proof = 0
        while not Verification.valid_proof(self.__open_transactions, last_hash, proof):
            proof += 1
        return proof

    def get_balance(self):
        """
        Calculates the balance for the hosting_node
        It takes into account explicitly all transactions that are pending mining in
        the open_transactions list.
        :return: A float that represents participant's balance.
        """
        participant = self.hosting_node
        tx_sender = [
            [tx.amount for tx in block.transactions if tx.sender == participant]
            for block in self.__chain
        ]

        open_tx_sender = [tx.amount for tx in self.__open_transactions if tx.sender == participant]
        tx_sender.append(open_tx_sender)

        amount_sent = reduce(lambda tx_sum, tx_amount: tx_sum + sum(tx_amount) if len(tx_amount) > 0 else tx_sum + 0,
                             tx_sender, 0)

        tx_recipient = [
            [tx.amount for tx in block.transactions if tx.recipient == participant]
            for block in self.__chain
        ]

        amount_received = reduce(
            lambda tx_sum, tx_amount: tx_sum + sum(tx_amount) if len(tx_amount) > 0 else tx_sum + 0, tx_recipient, 0)

        return amount_received - amount_sent

    def get_last_blockchain_value(self):
        """
        :return: Last blockchain value
        """

        if len(self.__chain) < 1:
            return None
        return self.__chain[-1]

    def add_transaction(self, recipient, sender, signature, amount=1.0):
        """
        Adds a new transaction to the open transaction's list.
        :param sender: The source of the transaction
        :param recipient: The destination of the transaction
        :param signature: The digital signature for this transaction.
        :param amount: The amount of coins sent with the transaction.
        :return: None
        """

        if not self.hosting_node:
            return False

        transaction = Transaction(sender, recipient, signature, amount)

        if Verification.verify_transaction(transaction, self.get_balance):
            self.__open_transactions.append(transaction)
            self.save_data()
            return True
        return False

    def mine_block(self):
        """
        Adds pending transactions to a block and appends it to the blockchain.

        :return: False if there were an error, True if mining was achieved.
        """
        if not self.hosting_node:
            return False

        last_block = self.__chain[-1]
        hashed_block = hash_block(last_block)

        proof = self.proof_of_work()

        # Important, the proof of work doesn't includes the reward transaction
        reward_transaction = Transaction('MINING', self.hosting_node, '', MINING_REWARD)

        copied_transactions = self.__open_transactions[:]
        for tx in copied_transactions:
            if not Wallet.verify_transaction(tx):
                return False
        copied_transactions.append(reward_transaction)

        block = Block(len(self.__chain), hashed_block, copied_transactions, proof)

        self.__chain.append(block)
        self.__open_transactions = []
        self.save_data()
        return True
