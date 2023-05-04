import sync, requests, json
from block import Block
from peer_config import *


def mine_block(new_block, rounds=STANDARD_ROUNDS, start_nonce=0):
    print("Mining for block %s. start_nonce: %s, rounds: %s" % (new_block.index, start_nonce, rounds))
    nonce_range = [i + start_nonce for i in range(rounds)]
    for nonce in nonce_range:
        new_block.nonce = nonce
        new_block.update_self_hash()
        if str(new_block.hash[0:NUM_ZEROS]) == '0' * NUM_ZEROS:
            print("block %s mined. Nonce: %s" % (new_block.index, new_block.nonce))
            assert new_block.is_valid()
            return new_block
    return None


def broadcast_mined_block(new_block):
    block_info_dict = new_block.to_dict()
    for peer in PEERS:
        endpoint = "%s%s" % (peer[0], peer[1])
        try:
            r = requests.post(peer + 'action/broadcasted_block', json=block_info_dict)
        except requests.exceptions.ConnectionError:
            print("Peer %s not connected" % peer)
            continue
    return True


def validate_broadcasted_block(broadcasted_block: Block):
    if broadcasted_block.is_valid():
        broadcasted_block.self_save()
        return True
    else:
        return False

