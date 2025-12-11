# test_nested_functions.py
import math

def outer_function(a, b):
    result = 0
    for i in range(a):
        if i % 2 == 0:
            for j in range(b):
                if j % 3 == 0:
                    for k in range(a):
                        if k % 2:
                            result += i * j * k
    return result

def middle_function(x):
    total = 0
    for i in range(x):
        if i % 2 == 0:
            for j in range(x):
                if j % 5 == 0:
                    total += i + j
    return total

def shallow_function(y):
    return y + 1

def another_nested_function(n):
    sum_val = 0
    for i in range(n):
        for j in range(n):
            if i != j:
                for k in range(n):
                    sum_val += i + j + k
    return sum_val

# Expected outcomes:
# - Metrics:
#     * Lines > 20
#     * Functions = 4
#     * Classes = 0
#     * Imports = 1
# - Class structure: none
# - Function structure: all 4 functions with their start/end lines, parameters, complexity calculated
# - Nesting depth: deep (outer_function & another_nested_function ≥ 4 levels)
# - Syntax errors: none
# - Style suggestions: none (no unused variables)
# - AST nodes: Assign, For, If, Call present
# - AST insights: many conditional statements and loops detected
# - Overall quality score: moderate (~50-70)
