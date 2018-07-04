from collections import OrderedDict
from utility.printable import Printable


class Transaction(Printable):
    """
    A transaction which can be added to a block in the blockchain.

    :param sender: The sender of the coins.
    :param recipient: The recipient of the coins.
    :param signature: Digital signature for this transaction.
    :param amount: The amount of coins sent.
    """
    def __init__(self, sender, recipient, signature, amount):
        self.sender = sender
        self.recipient = recipient
        self.amount = amount
        self.signature = signature

    def to_ordered_dict(self):
        return OrderedDict([('sender', self.sender), ('recipient', self.recipient), ('amount', self.amount)])