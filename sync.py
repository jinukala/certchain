from chain import Chain
from peer_config import *
import os,json, requests,glob,utils


def sync_refresh_local_chain():
    blocks = []
    if os.path.exists(CHAINDATA_DIR):
        for filepath in glob.glob(os.path.join(CHAINDATA_DIR, '*.json')):
            with open(filepath, 'r') as block_file:
                try:
                    block_data = json.load(block_file)
                    local_block = utils.generate_block(block_data)
                    blocks.append(local_block)
                except Exception as e:
                    print("FileSystem Error  ",e)
    local_chain = Chain(blocks)
    blocks.sort(key=lambda block: block.index)
    return local_chain


def sync_refresh_network_chain(save=False):
    best_chain = sync_refresh_local_chain()
    for peer in PEERS:
        peer_blockchain_url = peer + 'action/download'
        try:
            r = requests.get(peer_blockchain_url)
            peer_blockchain_data = r.json()
            peer_blocks = []
            for block in peer_blockchain_data:
                peer_blocks.append(utils.generate_block(block))
            peer_chain = Chain(peer_blocks)
            if peer_chain.is_valid() and len(peer_chain) > len(best_chain):
                best_chain = peer_chain

        except requests.exceptions.ConnectionError:
            print("Peer at %s not running. Continuing to next peer." % peer)
        else:
            print("Peer at %s is running. Gathered their blochchain for analysis." % peer)
    print("Longest blockchain is %s blocks" % len(best_chain))
    if save:
        best_chain.self_save()
    return best_chain


def sync(save=False):
    return sync_refresh_network_chain(save=save)
