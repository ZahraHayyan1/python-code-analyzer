from flask import Flask, render_template, request, send_file
import os
from fileRead import preprocess_python_file
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

    analyzer = CodeAnalyzer(code, file_path=file_path)
    analyzer.analyze()

    metrics = {
        "total_lines": analyzer.lines,
        "functions": analyzer.functions,
        "classes": analyzer.classes,
        "imports": analyzer.imports,
        "avg_complexity": analyzer.avg_complexity,
        "maintainability": analyzer.maintainability,
        "max_nesting": analyzer.max_nesting,
    }

    summary = (
        f"This Python file contains {metrics['total_lines']} lines, "
        f"{metrics['classes']} classes, {metrics['functions']} functions, "
        f"and {metrics['imports']} imports."
    )

    score = analyzer.calculate_quality_score()

    if score >= 80:
        quality_label = "Excellent Code Quality"
        quality_color = "green"
    elif score >= 50:
        quality_label = "Moderate Code Quality"
        quality_color = "yellow"
    else:
        quality_label = "Needs Improvement"
        quality_color = "red"

    results = {
        "file_name": file.filename,
        "summary": summary,
        "metrics": metrics,

        # NEW syntax checker output
        "syntax_check": {
            "has_error": len(analyzer.syntax_errors) > 0,
            "errors": analyzer.syntax_errors
        },

        "classes": analyzer.class_details,
        "functions": analyzer.function_details,
        "suggestions": analyzer.suggestions,

        "nodes": dict(analyzer.node_counts),
        "top_nodes": analyzer.top_nodes,
        "ast_insights": analyzer.ast_insights,

        "quality_percent": score,
        "quality_label": quality_label,
        "quality_color": quality_color,
    }

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




