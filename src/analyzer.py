from ast_parser import ASTParser

def generate_ast(code):
    parser = ASTParser(code)
    return parser.get_tree() #returns AST tree object
