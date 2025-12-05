from flask import Flask, render_template, request, redirect, url_for
import os

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/")
def upload_page():
    return render_template("upload.html")

@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return "No file part"

    file = request.files["file"]

    if file.filename == "":
        return "No selected file"

    if not file.filename.endswith(".py"):
        return "Invalid file type. Please upload a .py file."

    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(file_path)

    return redirect(url_for("results_page"))

@app.route("/results")
def results_page():
    return render_template(
        "results.html",
        lines=42,
        functions=3,
        classes=1,
        imports=2,
        error="None"
    )

if __name__ == "__main__":
    app.run(debug=True)