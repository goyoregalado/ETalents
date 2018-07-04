from utility.hash_util import hash_block, hash_string_256
from wallet import Wallet


class Verification:

    @staticmethod
    def valid_proof(transactions, last_hash, proof):
        """
        Checks if a combination of transactions, last_hash, and a number that it's represented by the proof
        argument pass the conditions of the proof of work algorithm.
        :param transactions: A list of transactions that we want to add to the blockchain
        :param last_hash: The hash of the last block
        :param proof: The number that we want to check as proof of work.
        :return:
        """
        guess = (str([tx.to_ordered_dict() for tx in transactions]) + str(last_hash) + str(proof)).encode()
        guess_hash = hash_string_256(guess)
        print('Trying hash: ', guess_hash)

        return guess_hash[0:2] == '00'

    @classmethod
    def verify_chain(cls, blockchain):
        """
        Verify the current blockchain and return True if it's valid of False if it's not.
        :param blockchain: A list of blocks that represents a blockchain structure.
        :return: A boolean, True if the blockchain is valid or False if it's not
        """
        for (index, block) in enumerate(blockchain):
            if index == 0:
                continue
            if block.previous_hash != hash_block(blockchain[index - 1]):
                return False
            # We exclude the reward transaction deliberately because when we computed
            # the proof of work hash we didn't take into account that block.
            if not cls.valid_proof(block.transactions[:-1], block.previous_hash, block.proof):
                print('Proof of work is invalid')
                return False
        return True

    @staticmethod
    def verify_transaction(transaction, get_balance, check_funds=True):
        """
        Verifies if the sender has enough funds to make a transaction.
        :param transaction: The transaction we want to verify.
        :param get_balance: A reference to a function that calculates the balance.
        :param check_funds: A boolean, if True forces to check the sender balance, if false it omits this check.
        :return: A boolean. True if the sender can perform the transaction false in other case.
        """
        if check_funds:
            sender_balance = get_balance()
            return sender_balance >= transaction.amount and Wallet.verify_transaction(transaction)
        else:
            return Wallet.verify_transaction(transaction)

    @classmethod
    def verify_transactions(cls, open_transactions, get_balance):
        """
        Verifies if all open_transactions are valid or not
        :param open_transactions: A list of open transactions
        :param get_balance: A reference to a function that calculates the balance.
        :return: True if all transactions are valid False in any other way.
        """
        return all([cls.verify_transaction(tx, get_balance, False) for tx in open_transactions])
