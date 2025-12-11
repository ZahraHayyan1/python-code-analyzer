# test_full_good.py
import math
import os

class Calculator:
    def add(self, a, b):
        return a + b

    def multiply(self, a, b):
        result = 0
        for _ in range(b):
            result += a
        return result

class AdvancedCalculator(Calculator):
    def power(self, base, exp):
        result = 1
        for _ in range(exp):
            result *= base
        return result

def greet(name):
    print(f"Hello, {name}!")

def compute_statistics(numbers):
    total = sum(numbers)
    count = len(numbers)
    mean = total / count if count else 0
    return mean

# Unused variable to trigger style suggestion
unused_var = 42

# Expected:
# - Metrics: lines>20, functions=5, classes=2, imports=2
# - Class structure: Calculator(2), AdvancedCalculator(1)
# - Function structure: all 5 functions, nested loops moderate
# - Nesting depth: 2-3
# - Syntax errors: none
# - Style suggestions: unused_var
# - AST nodes: Assign, Call, For
# - AST insights: many calls/assignments
# - Overall quality: high (~80-100)
