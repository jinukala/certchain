import hashlib, json, datetime
from peer_config import *


class Block(object):
    def __init__(self, index:int,timestamp:str,previous_hash:str,hash:str, data,reference_blocks,nonce:int):
        self.index = index
        self.previous_hash = previous_hash
        self.data = data
        self.reference_blocks = reference_blocks
        if timestamp is None:
            self.timestamp = datetime.datetime.utcnow().strftime('%Y/%m/%d-%H:%M:%S.%f')
        else:
            self.timestamp = timestamp
        if nonce is None:
            self.nonce = 0
        else:
            self.nonce = nonce
        if hash is None:
            self.hash = self.update_self_hash()
        else:
            self.hash = hash

    def header_string(self):
        return str(self.index) + self.previous_hash + str(self.data) + str(self.timestamp) + str(self.nonce)

    def generate_header(index, previous_hash, data, timestamp, nonce):
        return str(index) + previous_hash + data + str(timestamp) + str(nonce)

    def update_self_hash(self):
        sha = hashlib.sha512()
        sha.update(self.header_string().encode())
        new_hash = sha.hexdigest()
        self.hash = new_hash
        return new_hash

    def self_save(self):
        index_string = str(self.index).zfill(4)
        filename = '%s%s.json' % (CHAINDATA_DIR, index_string)
        with open(filename, 'w') as block_file:
            json.dump(self.to_dict(), block_file)

    def to_dict(self):
        info = {}
        info["index"] = str(self.index)
        info["timestamp"] = str(self.timestamp)
        info["previous_hash"] = str(self.previous_hash)
        info["hash"] = str(self.hash)
        try:
            info["data"] = json.loads(str(self.data))
            info["reference_blocks"] = json.loads(str(self.reference_blocks))
        except:
            info["data"] = self.data
            info["reference_blocks"] =self.reference_blocks
        info["nonce"] = str(self.nonce)
        return info

    def is_valid(self):
        possible_hash = self.get_hash()
        self.update_self_hash()
        if str(self.hash[0:NUM_ZEROS]) == '0' * NUM_ZEROS and self.get_hash() == possible_hash:
            return True
        else:
            return False

    def get_index(self):
        return self.index

    def get_hash(self):
        return self.hash

    def get_data(self):
        return self.data

    def get_reference_blocks(self):
        return self.reference_blocks

    def has_reference_blocks(self):
        if (self.reference_blocks) >0:
            return True
        return False

    def __repr__(self):
        return "Block<index: %s>, <hash: %s>" % (self.index, self.hash)

    def __eq__(self, other):
        return (self.index == other.index and
                self.timestamp == other.timestamp and
                self.previous_hash == other.previous_hash and
                self.hash == other.hash and
                self.data == other.data and
                self.nonce == other.nonce)

    def __ne__(self, other):
        return not self.__eq__(other)