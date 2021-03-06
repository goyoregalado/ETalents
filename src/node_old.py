from uuid import uuid4

from blockchain import Blockchain
from utility.verification import Verification
from wallet import Wallet


class Node:

    def __init__(self):
        # self.wallet.public_key = str(uuid4())
        self.wallet = Wallet()
        self.wallet.create_keys()
        self.blockchain = Blockchain(self.wallet.public_key)

    def get_transaction_value(self):
        """
        Ask's the user about a transaction's data.
        :return: Float formatted user input.
        """
        tx_recipient = input('Please, enter the recipient of the transaction: ')
        tx_amount = float(input('Please, enter the amount of the transaction: '))

        return tx_recipient, tx_amount

    def get_user_choice(self):
        user_input = input('Your choice: ')
        return user_input

    def print_blockchain_elements(self):
        for block in self.blockchain.chain:
            print('Outputting block: ')
            print(block)
        else:
            print('-' * 20)

    def listen_for_input(self):
        waiting_for_input = True
        while waiting_for_input:
            print('Please choose: ')
            print('1: Add a new transaction value')
            print('2: Mine a new block')
            print('3: Output the blockchain')
            print('4: Check transaction validity')
            print('5: Create wallet')
            print('6: Load wallet')
            print('7: Save wallet')
            print('q: Quit')
            user_choice = self.get_user_choice()

            if user_choice == '1':
                tx_data = self.get_transaction_value()
                recipient, amount = tx_data
                signature = self.wallet.sign_transaction(self.wallet.public_key, recipient, amount)
                if self.blockchain.add_transaction(recipient, self.wallet.public_key, signature, amount=tx_data[1]):
                    print('Added transaction')
                else:
                    print('Transaction rejected')

            elif user_choice == '2':
                if not self.blockchain.mine_block():
                    print('Mining failed!, check that you have a Wallet')

            elif user_choice == '3':
                self.print_blockchain_elements()

            elif user_choice == '4':
                if Verification.verify_transactions(self.blockchain.get_open_transactions(),
                                                    self.blockchain.get_balance):
                    print("All transactions are valid")
                else:
                    print("There are invalid transactions")

            elif user_choice == '5':
                self.wallet.create_keys()
                self.blockchain = Blockchain(self.wallet.public_key)

            elif user_choice == '6':
                self.wallet.load_keys()
                self.blockchain = Blockchain(self.wallet.public_key)

            elif user_choice == '7':
                self.wallet.save_keys()

            elif user_choice == 'q':
                waiting_for_input = False

            else:
                print('Invalid input, please select a value from the list')

            if not Verification.verify_chain(self.blockchain.chain):
                print('Invalid blockchain')
                break

            print("Balance for {} {:6.2f}".format(self.wallet.public_key, self.blockchain.get_balance()))

        else:
            print('User left!')

        print('Done!')


if __name__ == '__main__':
    node = Node()
    node.listen_for_input()
