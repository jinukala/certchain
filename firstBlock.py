import os
from schema import Certificate
from peer_config import *
import utils
import sync

data: Certificate = {
    "name": 'First Block',
    "parentName": "None",
    "registeredNumber": "None",
    "issuedDate": "01/01/1970",
    "stream": "None",
    "degree": "None",
    "institution": "None"
}


def mine_first_block():
    first_block = utils.create_new_block_from_previous(previous_block=None, data=data, reference_blocks=None)
    first_block.update_self_hash()
    while str(first_block.hash[0:NUM_ZEROS]) != '0' * NUM_ZEROS:
        first_block.nonce += 1
        first_block.update_self_hash()
    assert first_block.is_valid()
    return first_block


if __name__ == '__main__':

    if not os.path.exists(CHAINDATA_DIR):
        os.mkdir(CHAINDATA_DIR)

    if not os.listdir(CHAINDATA_DIR):
        first_block = mine_first_block()
        first_block.self_save()
    else:
        print("Chaindata directory already has files. If you want to generate a first block, delete files and rerun")
        sync.sync(save=True)
