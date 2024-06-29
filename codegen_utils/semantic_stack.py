class SemanticStack:
    def __init__(self):
        self.stack = []
        self.top = -1

    def push(self, item):
        self.stack.append(item)
        self.top += 1

    def pop(self):
        data = self.stack.pop()
        self.top -= 1
        return data

    def get_top(self):
        return self.top

    def peek(self, index):
        return self.stack[index]
