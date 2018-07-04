from hashlib import sha256
from json import dumps

#__all__ = ['hash_string_256', 'hash_block']


def hash_string_256(string):
    """
    Returns the sha256 hash of the argument
    :param string:
    :return: The sha256 hash of the argument
    """
    return sha256(string).hexdigest()


def hash_block(block):
    """
    Calculates a fake hash for a block.
    :param block: The block for which we are going to calc a fake hash
    :return: A fake hash
    """
    hashable_block = block.__dict__.copy()
    hashable_block['transactions'] = [tx.to_ordered_dict() for tx in hashable_block['transactions']]
    return sha256(dumps(hashable_block, sort_keys=True).encode()).hexdigest()