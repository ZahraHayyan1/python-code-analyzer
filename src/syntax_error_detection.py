import ast

def generate_hint(message: str) -> str:
    """Generates a simple fix hint based on common Python syntax errors."""
    msg = message.lower()

    if "unexpected eof" in msg or "unexpected end of file" in msg:
        return "You likely forgot to close a parenthesis, quote, or block."
    if "invalid syntax" in msg:
        return "Check for missing colon (:), parentheses, or indentation."
    if "expected ':'" in msg:
        return "Add a colon (:) at the end of the line."
    if "indentation" in msg:
        return "Check the indentation level (spaces/tabs)."
    if "unmatched" in msg:
        return "A bracket or parenthesis is not closed."
    if "cannot assign to" in msg:
        return "You used '=' where you should use '==' or expression is invalid."

    return "Fix the syntax on this line according to the error message."


def check_syntax(code: str):
    """
    Returns:
    {
        "has_error": bool,
        "error_count": int,
        "errors": [
            {
                "line": int,
                "column": int,
                "type": str,
                "message": str,
                "hint": str
            },
            ...
        ]
    }
    """

    errors = []

    try:
        ast.parse(code)
        return {
            "has_error": False,
            "error_count": 0,
            "errors": []
        }

    except SyntaxError as e:
        one_error = {
            "line": e.lineno,
            "column": e.offset,
            "type": e.__class__.__name__,
            "message": e.msg,
            "hint": generate_hint(e.msg),
        }

        errors.append(one_error)

        return {
            "has_error": True,
            "error_count": len(errors),
            "errors": errors
        }