import re
from pathlib import Path

def read_file(file_path: str) -> str:
    """Reads the content of a Python (.py) file."""
    path = Path(file_path)
    if not path.exists() or path.suffix != ".py":
        raise ValueError("Invalid file. Please provide a valid .py file.")

    # Try utf-8 first, fallback to cp1252
    try:
        with path.open("r", encoding="utf-8") as file:
            content = file.read()
    except UnicodeDecodeError:
        with path.open("r", encoding="cp1252") as file:
            content = file.read()

    return content


def clean_code(code: str) -> str:
    """Cleans Python code by removing comments and empty lines."""
    code_no_comments = re.sub(r'#.*', '', code)
    code_no_docstrings = re.sub(r'(""".*?"""|\'\'\'.*?\'\'\')', '', code_no_comments, flags=re.DOTALL)
    cleaned_code = "\n".join([line for line in code_no_docstrings.splitlines() if line.strip()])
    return cleaned_code


def preprocess_python_file(file_path: str):
    """Performs reading and cleaning steps only."""
    print(f" Reading file: {file_path}")
    code = read_file(file_path)

    print(" Cleaning code...")
    cleaned = clean_code(code)

    print(" Preprocessing completed (file ready for next stage).")
    return {
        "original_code": code,
        "cleaned_code": cleaned
    }


if __name__ == "__main__":
    file_path = r"C:\Users\hdool\Desktop\code_analizyr\fileRead\tst.py"
    result = preprocess_python_file(file_path)
    print("\nCleaned Code Preview:\n", result["cleaned_code"])
    input("\nPress Enter to exit...")
