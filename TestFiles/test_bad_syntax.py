# test_bad_syntax.py
import math
import os

class BrokenClass
    def add(self, a, b):
        return a + b

def missing_parenthesis(a, b:
    return a + b

def incomplete_string():
    s = "This string is not closed
    return s

# Expected outcomes:
# - Syntax errors detected:
#     * Class definition missing colon
#     * Function with missing parenthesis
#     * Unterminated string
# - All other analysis blocked:
#     * Metrics: Total Lines = 0, Functions = 0, Classes = 0, Imports = 0
#     * No class/function structure
#     * Nesting depth = 0
#     * Style suggestions = none
#     * AST nodes = none
#     * AST insights = none
#     * Overall quality score unavailable
