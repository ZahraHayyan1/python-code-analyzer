import ast
from dataclasses import dataclass
from typing import Dict

@dataclass
class CodeMetrics:
    total_lines: int
    function_count: int
    class_count: int
    import_count: int

class _MetricsVisitor(ast.NodeVisitor):
    
    def __init__(self) -> None:
        self.function_count = 0
        self.class_count = 0
        self.import_count = 0

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self.function_count += 1
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self.function_count += 1
        self.generic_visit(node)

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        self.class_count += 1
        self.generic_visit(node)

    def visit_Import(self, node: ast.Import) -> None:
        self.import_count += 1
        self.generic_visit(node) 

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        self.import_count += 1
        self.generic_visit(node)

def analyze_source(source_code: str) -> CodeMetrics:
    """
    Analyze a Python source string and return basic code metrics.
    This function does NOT handle syntax errors if the code is invalid,
    ast.parse() will raise SyntaxError (Task 5 can catch that).
    """
    #total number of lines (including empty & comments)
    total_lines = len(source_code.splitlines())

    tree = ast.parse(source_code)
    visitor = _MetricsVisitor()
    visitor.visit(tree)

    return CodeMetrics(
        total_lines=total_lines,
        function_count=visitor.function_count,
        class_count=visitor.class_count,
        import_count=visitor.import_count,
    )

def analyze_file(path: str) -> CodeMetrics:
    """
    Task 2 can call this after reading/uploading the file.
    """
    with open(path, "r", encoding="utf-8") as f:
        source = f.read()
    return analyze_source(source)

def metrics_to_dict(metrics: CodeMetrics) -> Dict[str, int]:
    return {
        "total_lines": metrics.total_lines,
        "function_count": metrics.function_count,
        "class_count": metrics.class_count,
        "import_count": metrics.import_count,
    }
