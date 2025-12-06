import ast

class ASTParser:
    def __init__(self, code):
        self.code = code
        self.tree = None

    def parse(self):
        self.tree = ast.parse(self.code)
        return self.tree

    def get_tree(self):
        if self.tree is None:
            self.parse()
        return self.tree