import ast
import collections
import inspect

try:
    from radon.complexity import cc_visit
    from radon.metrics import mi_visit
except ImportError:
    cc_visit = None
    mi_visit = None

try:
    from pylint import epylint as lint
except ImportError:
    lint = None

class CodeAnalyzer(ast.NodeVisitor):
    def __init__(self, code, file_path=None):
        self.code = code
        self.file_path = file_path
        self.tree = None
        self.lines = 0
        self.functions = 0
        self.classes = 0
        self.imports = 0
        self.error = None
        self.error_type = None
        self.error_line = None
        self.error_msg = None
        self.nodes = []
        self.node_counts = collections.Counter()
        self.avg_complexity = None
        self.maintainability = None
        self.max_nesting = 0
        self.function_details = []
        self.class_details = []
        self.suggestions = []
        self.complexity_map = {}

    def analyze(self):
        try:
            self.tree = ast.parse(self.code)
        except SyntaxError as e:
            self.error = e
            self.error_type = e.msg
            self.error_line = e.lineno
            self.error_msg = e.text
            return
        self.lines = len(self.code.splitlines())
        self.visit(self.tree)
        self._compute_nesting(self.tree, 0)
        self._analyze_complexity()
        self._build_details()
        self._analyze_pylint()

    def visit(self, node):
        node_type = type(node).__name__
        self.nodes.append(node_type)
        self.node_counts[node_type] += 1
        super().visit(node)

    def visit_FunctionDef(self, node):
        self.functions += 1
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node):
        self.functions += 1
        self.generic_visit(node)

    def visit_ClassDef(self, node):
        self.classes += 1
        self.generic_visit(node)

    def visit_Import(self, node):
        self.imports += 1

    def visit_ImportFrom(self, node):
        self.imports += 1

    def _compute_nesting(self, node, depth):
        block_types = (
            ast.If,
            ast.For,
            ast.While,
            ast.With,
            ast.Try,
            ast.FunctionDef,
            ast.AsyncFunctionDef,
            ast.ClassDef,
        )
        if isinstance(node, block_types):
            depth += 1
            if depth > self.max_nesting:
                self.max_nesting = depth
        for child in ast.iter_child_nodes(node):
            self._compute_nesting(child, depth)

    def _analyze_complexity(self):
        if cc_visit is None:
            return
        try:
            blocks = cc_visit(self.code)
            values = []
            for b in blocks:
                values.append(b.complexity)
                key = (b.name, b.lineno)
                self.complexity_map[key] = b.complexity
            if values:
                self.avg_complexity = sum(values) / len(values)
        except Exception:
            pass
        if mi_visit is None:
            return
        try:
            score = mi_visit(self.code, False)
            self.maintainability = score
        except Exception:
            pass

    def _build_details(self):
        if self.tree is None:
            return
        functions = []
        classes = []
        for node in ast.walk(self.tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                end_lineno = getattr(node, "end_lineno", node.lineno)
                loc = end_lineno - node.lineno + 1
                args = [a.arg for a in node.args.args]
                key = (node.name, node.lineno)
                complexity = self.complexity_map.get(key)
                functions.append(
                    {
                        "name": node.name,
                        "line": node.lineno,
                        "end_line": end_lineno,
                        "loc": loc,
                        "args": args,
                        "complexity": complexity,
                    }
                    )
            if isinstance(node, ast.ClassDef):
                end_lineno = getattr(node, "end_lineno", node.lineno)
                loc = end_lineno - node.lineno + 1
                methods = [
                    n
                    for n in node.body
                    if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
                ]
                classes.append(
                    {
                        "name": node.name,
                        "line": node.lineno,
                        "end_line": end_lineno,
                        "loc": loc,
                        "methods_count": len(methods),
                    }
                )
        self.function_details = sorted(functions, key=lambda x: x["line"])
        self.class_details = sorted(classes, key=lambda x: x["line"])

    def _analyze_pylint(self):
        if lint is None or not self.file_path:
            return
        try:
            pout, perr = lint.py_run(self.file_path, return_std=True)
            text = pout.getvalue()
            suggestions = []
            for line in text.splitlines():
                if ":" not in line:
                    continue
                parts = line.split(":", 4)
                if len(parts) < 5:
                    continue
                path, lineno, col, msg_id, msg = parts
                entry = {
                    "line": int(lineno) if lineno.strip().isdigit() else None,
                    "code": msg_id.strip(),
                    "message": msg.strip(),
                }
                suggestions.append(entry)
            self.suggestions = suggestions
        except Exception:
            pass