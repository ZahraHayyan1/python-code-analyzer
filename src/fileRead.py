import re
from pathlib import Path

def read_file(file_path):
    path = Path(file_path)
    if not path.exists() or path.suffix != ".py":
        raise ValueError("Invalid file")
    try:
        with path.open("r", encoding="utf-8") as file:
            content = file.read()
    except UnicodeDecodeError:
        with path.open("r", encoding="cp1252") as file:
            content = file.read()
    return content

def clean_code(code):
    code_no_comments = re.sub(r"#.*", "", code)
    code_no_docstrings = re.sub(r'(""".*?"""|\'\'\'.*?\'\'\')', "", code_no_comments, flags=re.DOTALL)
    cleaned_code = "\n".join([line for line in code_no_docstrings.splitlines() if line.strip()])
    return cleaned_code

def preprocess_python_file(file_path):
    code = read_file(file_path)
    cleaned = clean_code(code)
    return {
        "original_code": code,
        "cleaned_code": cleaned
    }

if __name__ == "__main__":
    pass
