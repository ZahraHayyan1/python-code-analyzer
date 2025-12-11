# test_full_bad.py
import sys
import os

class ComplexCalculator:
    def crazy_method(self, n):
        total = 0
        for i in range(n):
            if i % 2 == 0:
                for j in range(n):
                    if j % 3 == 0:
                        total += i * j
        return total

    def unused_method(self):
        x = 10
        y = 20
        z = 30
        return 0

class EmptyClass:
    pass

def nested_function(a, b, c, d):
    result = 0
    for i in range(a):
        if i % 2 == 0:
            for j in range(b):
                if j % 3 == 0:
                    for k in range(c):
                        if k % 2:
                            result += i + j + k
    return result + d

def shallow_function():
    temp = 100  # unused variable
    return 1

unused_global = 99  # unused

# Expected:
# - Metrics: lines>30, functions=4, classes=2, imports=2
# - Class structure: ComplexCalculator(2 methods), EmptyClass(0)
# - Function structure: nested_function → deep nesting
# - Nesting depth: 4+
# - Syntax errors: none
# - Style suggestions: x, y, z, temp, unused_global
# - AST nodes: Assign, For, If, Call
# - AST insights: many conditionals and assignments
# - Overall quality: low (~20-50)
