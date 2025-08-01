import ast

def get_function_names(filename):
    with open(filename, "r") as f:
        tree = ast.parse(f.read(), filename=filename)
    return [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]

