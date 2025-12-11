import ast
from code_analyzer_module import CodeAnalyzer  # غيّر 'code_analyzer_module' لاسم الملف اللي فيه الكود الأصلي

# مثال كود لاختباره
sample_code = """
def foo(x):
    if x > 0:
        return x * 2
    else:
        return x - 2

class Bar:
    def method(self):
        for i in range(5):
            print(i)
"""

def test_ast_analysis(code: str):
    analyzer = CodeAnalyzer(code)
    analyzer.analyze()

    print("------ AST Nodes Counts ------")
    for node, count in analyzer.node_counts.items():
        print(f"{node}: {count}")

    print("\n------ Top Nodes ------")
    for node, count in analyzer.top_nodes.items():
        print(f"{node}: {count}")

    print("\n------ Function Details ------")
    for f in analyzer.function_details:
        print(f)

    print("\n------ Class Details ------")
    for c in analyzer.class_details:
        print(c)

    print("\n------ AST Insights ------")
    for insight in analyzer.ast_insights:
        print("-", insight)

    print("\n------ Max Nesting ------")
    print(analyzer.max_nesting)

    print("\n------ Quality Score ------")
    print(analyzer.calculate_quality_score())

if __name__ == "__main__":
    test_ast_analysis(sample_code)