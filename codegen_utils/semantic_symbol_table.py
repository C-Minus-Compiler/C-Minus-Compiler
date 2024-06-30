from enum import Enum

class SymbolTableEntryType(Enum):
    FUNC = "func"
    VAR = "var"
    INT = "int"
    VOID = "void"
    ARR = "arr"
    
    @classmethod
    def get_type_by_lexeme(cls, lexeme):
        if lexeme == "int":
            return SymbolTableEntryType.INT 
        elif lexeme == "void":
            return SymbolTableEntryType.VOID
        return None

class SymbolTableEntry:
    def __init__(self, lexeme, address, scope):
        self.lexeme = lexeme
        self.address = address
        self.scope = scope
        self.types = []
        self.size = 1
    
    def add_type(self, typ):
        self.types.append(typ)

    def set_size(self, size):
        self.size = size
    
    def set_address(self, addr):
        self.address = addr

class SemanticSymbolTable:
    def __init__(self) -> None:
        self.table = []

    def insert_variable(self, variable):
        self.table.append(variable)

    def insert_entry(self, entry):
        self.table.append(entry)
    
    def find_variable(self, variable_name):
        for variable in reversed(self.table):
            if variable.lexeme == variable_name:
                return variable

    def find_by_address(self, addr):
        for e in reversed(self.table):
            if e.address == addr:
                return e
        return None

    def find_by_lexeme(self, lex):
        for e in reversed(self.table):
            if e.lexeme == lex:
                return e
        return None
