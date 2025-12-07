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
            ast.If, ast.For, ast.While, ast.With, ast.Try,
            ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef
        )

        if isinstance(node, block_types):
            depth += 1
            self.max_nesting = max(self.max_nesting, depth)

        for child in ast.iter_child_nodes(node):
            self._compute_nesting(child, depth)

    # -----------------------------------------------------
    # Local nesting per function
    # -----------------------------------------------------

    def _compute_local_nesting(self, fn_node):
        max_depth = 0

        def walk(node, depth):
            nonlocal max_depth
            block_types = (ast.If, ast.For, ast.While, ast.With, ast.Try)
            if isinstance(node, block_types):
                depth += 1
                max_depth = max(max_depth, depth)
            for child in ast.iter_child_nodes(node):
                walk(child, depth)

        walk(fn_node, 0)
        return max_depth

    # -----------------------------------------------------
    # Score each function individually
    # -----------------------------------------------------

    def _score_function(self, complexity, loc, params, nesting):
        # Complexity (40%)
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

        # Length (25%)
        if loc <= 10:
            ln = 25
        elif loc <= 20:
            ln = 18
        elif loc <= 30:
            ln = 12
        else:
            ln = 5

        # Parameters (20%)
        if params <= 2:
            pm = 20
        elif params <= 4:
            pm = 14
        else:
            pm = 6

        # Nesting (15%)
        if nesting <= 2:
            ns = 15
        elif nesting <= 4:
            ns = 10
        else:
            ns = 5

        return cx + ln + pm + ns

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
                nesting = self._compute_local_nesting(node)
                quality = self._score_function(complexity, loc, len(args), nesting)

                functions.append({
                    "name": node.name,
                    "line": node.lineno,
                    "end_line": end_line,
                    "loc": loc,
                    "args": args,
                    "complexity": complexity,
                    "quality": quality,
                })

            if isinstance(node, ast.ClassDef):
                end_line = getattr(node, "end_lineno", node.lineno)
                loc = end_line - node.lineno + 1
                methods = [
                    n for n in node.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
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
    # FIXED & FINAL pylint analyzer
    # -----------------------------------------------------

    def _analyze_pylint(self):
        self.suggestions = []

        if lint is None or not self.file_path:
            return

        try:
            stdout, stderr = lint.py_run(
                f"{self.file_path} --score=no --output-format=text",
                return_std=True
            )

            # 🔥 Combine BOTH stdout + stderr
            text = (stdout.getvalue() or "") + "\n" + (stderr.getvalue() or "")
            output = text.strip().splitlines()

            for line in output:
                if ":" not in line:
                    continue

                parts = line.split(":", 3)
                if len(parts) < 4:
                    continue

                filepath, lineno, col, remainder = parts
                lineno = lineno.strip()

                if " " not in remainder:
                    continue

                msg_id, msg_text = remainder.split(" ", 1)

                self.suggestions.append({
                    "line": int(lineno) if lineno.isdigit() else None,
                    "code": msg_id.strip(),
                    "message": msg_text.strip(),
                })

        except Exception as e:
            self.suggestions.append({
                "line": None,
                "code": "PylintError",
                "message": f"Pylint could not run: {e}"
            })

    # -----------------------------------------------------

    def _extract_top_nodes(self):
        wanted = [
            "Name", "Assign", "Call", "If", "For", "While",
            "Return", "Attribute", "BinOp", "Try"
        ]
        self.top_nodes = {n: self.node_counts.get(n, 0) for n in wanted}

    # -----------------------------------------------------

    def _generate_ast_insights(self):
        insights = []
        loc = max(1, self.lines)

        def is_high(count, factor):
            return count >= (loc / factor)

        tn = self.top_nodes

        if is_high(tn["If"], 15):
            insights.append("Many conditional statements — try simplifying logic.")
        if is_high(tn["Call"], 12):
            insights.append("Large number of function calls — may indicate repeated work.")
        if is_high(tn["Assign"], 20):
            insights.append("Many assignments — try grouping logic.")

        self.ast_insights = insights

    # -----------------------------------------------------

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
