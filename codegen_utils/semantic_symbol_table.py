class SemanticSymbolTable:
    def __init__(self) -> None:
        self.variables = []

    def insert_variable(self, variable):
        self.variables.append(variable)

    def find_variable(self, variable_name):
        for variable in self.variables:
            if variable.name == variable_name:
                return variable
