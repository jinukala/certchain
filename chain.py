from block import Block
import sync

class Chain(object):
    def __init__(self, blocks: list[Block]):
        self.blocks = blocks

    def is_valid(self):
        for index, current_block in enumerate(self.blocks[1:]):
            previous_block = self.blocks[index]
            if previous_block.index + 1 != current_block.index:
                print('index error')
                return False
            if not current_block.is_valid():
                print('block invalid')
                return False
            if previous_block.hash != current_block.previous_hash:
                print('hash error')
                return False
        return True

    def self_save(self):
        for b in self.blocks:
            b.self_save()
        return True

    def find_block_by_index(self, index):
        if len(self) <= index:
            return self.blocks[index]
        else:
            return False

    def find_block_by_hash(self, hash):
        for b in self.blocks:
            if b.hash == hash:
                return b
        return False

    def __len__(self):
        return len(self.blocks)

    def __eq__(self, other):
        if len(self) != len(other):
            return False
        for self_block, other_block in zip(self.blocks, other.blocks):
            if self_block != other_block:
                return False
        return True

    def __ne__(self, other):
        return not self.__eq__(other)

    def most_recent_block(self):
        return self.blocks[-1]

    def max_index(self):
        return self.blocks[-1].index

    def add_block(self, new_block):
        if new_block.get_index() < self.max_index():
            return False
        self.blocks.append(new_block)
        return True

    def block_list_dict(self):
        return [b.to_dict() for b in self.blocks]

    def update_chain(self):
        self.blocks = sync.sync_refresh_local_chain().blocks
