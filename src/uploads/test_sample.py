import math
import os

# Missing newline here on purpose

def add_numbers(a, b,c):  # too many params, spacing issues
    if a > 10:
            if b > 5:
                    return a + b + c
    else:
        return a-b

def buggy_function(x):
    for i in range(5):
        if i % 2 == 0:
                print("Even")
        else:
             print("Odd")

    try:
            risky_operation = x / 0   # division by zero warning
    except:
        pass

class SampleClass:
    def method_one(self, x):
            if x > 0:
                    return x * 2
            return x

    def method_two(self):
        for i in range(3):
            print(i)

# Function with unnecessary complexity
def nested():
    for i in range(3):
        for j in range(2):
            if i == j:
                print("Match")
            else:
                if j == 1:
                    if i == 2:
                        print("Deep nesting")

# Intentional bad formatting and unused variable
def messy():
  x=5
  y = 10
  return x+ y
