import ast
import collections

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


def generate_hint(message: str) -> str:
    msg = message.lower()
    if "unexpected eof" in msg or "unexpected end of file" in msg:
        return "You may have missed closing a parenthesis, quote, or block."
    if "invalid syntax" in msg:
        return "Check for missing colon, parenthesis, or incorrect indentation."
    if "expected ':'" in msg:
        return "Add a colon ':' at the end of the statement."
    if "indentation" in msg:
        return "Verify indentation levels."
    if "unmatched" in msg:
        return "A bracket or parenthesis is not closed."
    if "cannot assign to" in msg:
        return "You may have used '=' instead of '==' or assigned to an invalid expression."
    return "Fix the syntax on this line according to the error."


def check_syntax(code: str):
    errors = []
    try:
        ast.parse(code)
        return {"has_error": False, "error_count": 0, "errors": []}
    except SyntaxError as e:
        one_error = {
            "line": e.lineno,
            "column": e.offset,
            "type": e.__class__.__name__,
            "message": e.msg,
            "hint": generate_hint(e.msg)
        }
        errors.append(one_error)
        return {
            "has_error": True,
            "error_count": len(errors),
            "errors": errors
        }


class CodeAnalyzer(ast.NodeVisitor):
    def __init__(self, code, file_path=None):
        self.code = code
        self.file_path = file_path
        self.tree = None

        self.lines = 0
        self.functions = 0
        self.classes = 0
        self.imports = 0

        self.syntax_errors = []
        self.suggestions = []

        self.nodes = []
        self.node_counts = collections.Counter()

        self.avg_complexity = None
        self.maintainability = None
        self.max_nesting = 0

        self.function_details = []
        self.class_details = []
        self.complexity_map = {}

        self.top_nodes = {}
        self.ast_insights = []

    def analyze(self):
        syntax = check_syntax(self.code)
        if syntax["has_error"]:
            self.syntax_errors = syntax["errors"]
            return

        try:
            self.tree = ast.parse(self.code)
        except SyntaxError:
            return

        self.lines = len(self.code.splitlines())

        self.visit(self.tree)
        self._compute_nesting(self.tree, 0)
        self._analyze_complexity()
        self._build_details()
        self._analyze_pylint()
        self._extract_top_nodes()
        self._generate_ast_insights()

    def visit(self, node):
        t = type(node).__name__
        self.nodes.append(t)
        self.node_counts[t] += 1
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
        blocks = (
            ast.If, ast.For, ast.While, ast.With, ast.Try,
            ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef
        )
        if isinstance(node, blocks):
            depth += 1
            self.max_nesting = max(self.max_nesting, depth)
        for child in ast.iter_child_nodes(node):
            self._compute_nesting(child, depth)

    def _compute_local_nesting(self, fn):
        max_depth = 0
        def walk(n, d):
            nonlocal max_depth
            blocks = (ast.If, ast.For, ast.While, ast.With, ast.Try)
            if isinstance(n, blocks):
                d += 1
                max_depth = max(max_depth, d)
            for c in ast.iter_child_nodes(n):
                walk(c, d)
        walk(fn, 0)
        return max_depth

    def _score_function(self, complexity, loc, params, nesting):
        if complexity is None:
            cx = 20
        elif complexity <= 3:
            cx = 40
        elif complexity <= 6:
            cx = 30
        elif complexity <= 10:
            cx = 20
        else:
            cx = 10

        if loc <= 10:
            ln = 25
        elif loc <= 20:
            ln = 18
        elif loc <= 30:
            ln = 12
        else:
            ln = 5

        if params <= 2:
            pm = 20
        elif params <= 4:
            pm = 14
        else:
            pm = 6

        if nesting <= 2:
            ns = 15
        elif nesting <= 4:
            ns = 10
        else:
            ns = 5

        return cx + ln + pm + ns

    def _analyze_complexity(self):
        if cc_visit:
            try:
                blocks = cc_visit(self.code)
                values = []
                for b in blocks:
                    values.append(b.complexity)
                    self.complexity_map[(b.name, b.lineno)] = b.complexity
                if values:
                    self.avg_complexity = sum(values) / len(values)
            except:
                pass

        if mi_visit:
            try:
                self.maintainability = mi_visit(self.code, False)
            except:
                pass

    def _build_details(self):
        if self.tree is None:
            return
        functions = []
        classes = []
        for node in ast.walk(self.tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                end = getattr(node, "end_lineno", node.lineno)
                loc = end - node.lineno + 1
                args = [a.arg for a in node.args.args]
                c = self.complexity_map.get((node.name, node.lineno))
                nest = self._compute_local_nesting(node)
                q = self._score_function(c, loc, len(args), nest)
                functions.append({
                    "name": node.name,
                    "line": node.lineno,
                    "end_line": end,
                    "loc": loc,
                    "args": args,
                    "complexity": c,
                    "quality": q
                })
            if isinstance(node, ast.ClassDef):
                end = getattr(node, "end_lineno", node.lineno)
                loc = end - node.lineno + 1
                m = [
                    n for n in node.body
                    if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
                ]
                classes.append({
                    "name": node.name,
                    "line": node.lineno,
                    "end_line": end,
                    "loc": loc,
                    "methods_count": len(m)
                })
        self.function_details = sorted(functions, key=lambda x: x["line"])
        self.class_details = sorted(classes, key=lambda x: x["line"])

    def _analyze_pylint(self):
        self.suggestions = []
        if lint is None or not self.file_path:
            return
        try:
            stdout, stderr = lint.py_run(
                f"{self.file_path} --score=no --output-format=text",
                return_std=True
            )
            text = (stdout.getvalue() or "") + "\n" + (stderr.getvalue() or "")
            lines = text.strip().splitlines()

            for line in lines:
                if ":" not in line:
                    continue
                parts = line.split(":", 3)
                if len(parts) < 4:
                    continue
                _, lineno, _, message = parts
                lineno = lineno.strip()
                if " " not in message:
                    continue
                msg_id, msg_text = message.split(" ", 1)
                self.suggestions.append({
                    "line": int(lineno) if lineno.isdigit() else None,
                    "code": msg_id.strip(),
                    "message": msg_text.strip()
                })
        except:
            pass

    def _extract_top_nodes(self):
        wanted = [
            "Name", "Assign", "Call", "If", "For", "While",
            "Return", "Attribute", "BinOp", "Try"
        ]
        self.top_nodes = {n: self.node_counts.get(n, 0) for n in wanted}

    def _generate_ast_insights(self):
        insights = []
        loc = max(1, self.lines)

        def high(c, f):
            return c >= (loc / f)

        tn = self.top_nodes
        if high(tn["If"], 15):
            insights.append("Many conditional statements detected.")
        if high(tn["Call"], 12):
            insights.append("High number of function calls detected.")
        if high(tn["Assign"], 20):
            insights.append("Many assignments detected.")
        self.ast_insights = insights

    def calculate_quality_score(self):
        score = 100
        if self.avg_complexity is not None:
            score -= min(40, self.avg_complexity * 5)
        if self.maintainability is not None:
            if self.maintainability < 50:
                score -= 25
            elif self.maintainability < 70:
                score -= 10
        score -= min(20, self.max_nesting * 4)
        return max(0, min(100, int(score)))

