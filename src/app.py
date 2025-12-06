from flask import Flask, render_template, request, send_file
import os
from fileRead import preprocess_python_file
from ast_parser import ASTParser
from analyzer import CodeAnalyzer
from report_generator import generate_report

base_dir = os.path.dirname(__file__)

app = Flask(
    __name__,
    template_folder=os.path.join(base_dir, "templates"),
    static_folder=os.path.join(base_dir, "static"),
)

UPLOAD_FOLDER = os.path.join(base_dir, "uploads")
REPORT_FOLDER = os.path.join(base_dir, "reports")

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(REPORT_FOLDER, exist_ok=True)


@app.route("/")
def upload_page():
    return render_template("upload.html")


@app.route("/upload", methods=["POST"])
def upload_file():
    file = request.files.get("file")

    if not file or file.filename == "" or not file.filename.endswith(".py"):
        return render_template("upload.html", error="Please upload a valid .py file.")

    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(file_path)

    processed = preprocess_python_file(file_path)
    code = processed["cleaned_code"]

    parser = ASTParser(code)
    parser.get_tree()

    analyzer = CodeAnalyzer(code, file_path=file_path)
    analyzer.analyze()

    # --------------------------
    # METRICS
    # --------------------------
    metrics = {
        "total_lines": analyzer.lines,
        "functions": analyzer.functions,
        "classes": analyzer.classes,
        "imports": analyzer.imports,
        "avg_complexity": analyzer.avg_complexity,
        "maintainability": analyzer.maintainability,
        "max_nesting": analyzer.max_nesting,
    }

    syntax = {
        "error": analyzer.error is not None,
        "error_type": analyzer.error_type,
        "line": analyzer.error_line,
        "msg": analyzer.error_msg or "",
    }

    summary = (
        f"This Python file contains {metrics['total_lines']} lines, "
        f"{metrics['classes']} classes, {metrics['functions']} functions, "
        f"and {metrics['imports']} imports."
    )

    # --------------------------
    # QUALITY SCORE SYSTEM
    # --------------------------
    score = 0

    # Maintainability score
    if metrics["maintainability"]:
        if metrics["maintainability"] >= 80:
            score += 40
        elif metrics["maintainability"] >= 60:
            score += 30
        elif metrics["maintainability"] >= 40:
            score += 20
        else:
            score += 10

    # Complexity score (lower is better)
    if metrics["avg_complexity"]:
        if metrics["avg_complexity"] <= 3:
            score += 40
        elif metrics["avg_complexity"] <= 6:
            score += 30
        elif metrics["avg_complexity"] <= 10:
            score += 20
        else:
            score += 10

    # Nesting score (lower is better)
    nesting = metrics["max_nesting"]
    if nesting <= 2:
        score += 20
    elif nesting <= 4:
        score += 15
    elif nesting <= 6:
        score += 10
    else:
        score += 5

    quality_percent = min(score, 100)

    if quality_percent >= 80:
        quality_label = "Excellent Code Quality"
        quality_color = "green"
    elif quality_percent >= 50:
        quality_label = "Moderate Code Quality"
        quality_color = "yellow"
    else:
        quality_label = "Needs Improvement"
        quality_color = "red"

    # --------------------------
    # RESULTS PACKAGE
    # (✨ Added: top_nodes + ast_insights)
    # --------------------------
    results = {
        "file_name": file.filename,
        "summary": summary,
        "metrics": metrics,
        "syntax": syntax,
        "classes": analyzer.class_details,
        "functions": analyzer.function_details,
        "suggestions": analyzer.suggestions,
        "nodes": dict(analyzer.node_counts),

        # NEW — AST Node Summary + Insights
        "top_nodes": analyzer.top_nodes,
        "ast_insights": analyzer.ast_insights,

        # Quality Score
        "quality_percent": quality_percent,
        "quality_label": quality_label,
        "quality_color": quality_color,
    }

    # --------------------------
    # GENERATE REPORT FILE
    # --------------------------
    report_name = f"{os.path.splitext(file.filename)[0]}_report.html"
    report_path = os.path.join(REPORT_FOLDER, report_name)
    generate_report(results, output_path=report_path)

    return render_template("results.html", report_file=report_name, **results)


@app.route("/download-report/<filename>")
def download_report(filename):
    path = os.path.join(REPORT_FOLDER, filename)
    if not os.path.exists(path):
        return "Report not found", 404
    return send_file(path, as_attachment=True)


if __name__ == "__main__":
    app.run(debug=True)

