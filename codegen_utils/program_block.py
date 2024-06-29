class ProgramBlock:
    def __init__(self):
        self.blocks = []
        self.block_pointer = 0

    def add_block(self, block):
        self.blocks.append(block)
        self.block_pointer += 1

    def set_block(self, block, i):
        self.blocks[i] = block

    def increase_block_pointer(self):
        self.block_pointer += 1
        return self.block_pointer

    def add_empty_block(self):
        self.blocks.append(None)
        self.block_pointer = 1
