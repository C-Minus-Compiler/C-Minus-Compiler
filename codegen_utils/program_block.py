class ProgramBlock:

    def __init__(self):
        self.blocks = []
        self.block_pointer = 0

    def add_block(self, block):
        self.blocks.append(block)
        self.block_pointer += 1

    def add_block_with_index(self, block, index):
        self.blocks[index] = block

    def add_empty_block(self):
        self.blocks.append(None)
        self.block_pointer = 1
