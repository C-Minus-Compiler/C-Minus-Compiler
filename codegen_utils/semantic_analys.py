class Function:
    def __init__(self, name, return_type, program_address):
        self.name = name 
        self.return_type = return_type
        self.program_address = program_address
        self.params = []
    def add_param(self, param):
        self.params.append(param)

    def have_param(self, lexeme):
        for p in self.params:
            if p.lexeme == lexeme:
                return True
        return False

class Parameter:
    def __init__(self, lexeme, typ, is_arr):
        self.lexeme = lexeme
        self.typ = typ
        self.is_arr = is_arr

    
