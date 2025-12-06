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

        # New:
        self.top_nodes = {}
        self.ast_insights = []

    # -----------------------------------------------------

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
        self._extract_top_nodes()
        self._generate_ast_insights()

    # -----------------------------------------------------

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

    # -----------------------------------------------------

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
            self.max_nesting = max(self.max_nesting, depth)

        for child in ast.iter_child_nodes(node):
            self._compute_nesting(child, depth)

    # -----------------------------------------------------

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

            except Exception:
                pass

        if mi_visit:
            try:
                self.maintainability = mi_visit(self.code, False)
            except Exception:
                pass

    # -----------------------------------------------------

    def _build_details(self):
        if self.tree is None:
            return

        functions = []
        classes = []

        for node in ast.walk(self.tree):

            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                end_line = getattr(node, "end_lineno", node.lineno)
                loc = end_line - node.lineno + 1
                args = [a.arg for a in node.args.args]
                complexity = self.complexity_map.get((node.name, node.lineno))

                functions.append({
                    "name": node.name,
                    "line": node.lineno,
                    "end_line": end_line,
                    "loc": loc,
                    "args": args,
                    "complexity": complexity,
                })

            if isinstance(node, ast.ClassDef):
                end_line = getattr(node, "end_lineno", node.lineno)
                loc = end_line - node.lineno + 1

                methods = [
                    n for n in node.body
                    if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
                ]

                classes.append({
                    "name": node.name,
                    "line": node.lineno,
                    "end_line": end_line,
                    "loc": loc,
                    "methods_count": len(methods),
                })

        self.function_details = sorted(functions, key=lambda x: x["line"])
        self.class_details = sorted(classes, key=lambda x: x["line"])

    # -----------------------------------------------------

    def _analyze_pylint(self):
        if lint is None or not self.file_path:
            return

        try:
            pout, _ = lint.py_run(self.file_path, return_std=True)
            text = pout.getvalue()
            results = []

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
                results.append(entry)

            self.suggestions = results

        except Exception:
            pass

    # -----------------------------------------------------
    # NEW — extract top 10 node types
    # -----------------------------------------------------

    def _extract_top_nodes(self):

        wanted = [
            "Name",
            "Assign",
            "Call",
            "If",
            "For",
            "While",
            "Return",
            "Attribute",
            "BinOp",
            "Try",
        ]

        result = {}

        for n in wanted:
            result[n] = self.node_counts.get(n, 0)

        self.top_nodes = result

    # -----------------------------------------------------
    # NEW — generate AST insights based on node frequency
    # -----------------------------------------------------

    def _generate_ast_insights(self):
        insights = []
        loc = max(1, self.lines)

        # thresholds strict
        def is_high(count, factor):
            return count >= (loc / factor)

        tn = self.top_nodes

        # ---- Rules ----

        if is_high(tn["If"], 15):
            insights.append("High number of conditional branches (if-statements). Consider simplifying logic or reducing nested conditions.")

        if is_high(tn["For"], 25) or is_high(tn["While"], 25):
            insights.append("Frequent loops detected. Might indicate heavy iteration—consider optimizing loops or using vectorized operations (like Python builtins).")

        if is_high(tn["Call"], 12):
            insights.append("Large number of function calls. Ensure functions are necessary and check for repeated patterns that could be refactored.")

        if is_high(tn["Assign"], 20):
            insights.append("Many variable assignments. Consider reducing temporary variables or grouping related logic.")

        if is_high(tn["Attribute"], 20):
            insights.append("High attribute access count. Code may be too object-heavy or performing repeated property lookups.")

        if is_high(tn["BinOp"], 30):
            insights.append("Many arithmetic/logic operations. Consider simplifying expressions or breaking them into readable steps.")

        if is_high(tn["Try"], 40):
            insights.append("Frequent try/except blocks detected. Could signal error-prone code or overly defensive programming.")

        # final assignment:
        self.ast_insights = insights

    # -----------------------------------------------------
    # NEW — Overall quality score
    # -----------------------------------------------------

    def calculate_quality_score(self):
        score = 100

        # Complexity impact
        if self.avg_complexity is not None:
            score -= min(40, self.avg_complexity * 5)

        # Maintainability impact
        if self.maintainability is not None:
            if self.maintainability < 50:
                score -= 25
            elif self.maintainability < 70:
                score -= 10

        # Nesting depth impact
        score -= min(20, self.max_nesting * 4)

        return max(0, min(100, int(score)))