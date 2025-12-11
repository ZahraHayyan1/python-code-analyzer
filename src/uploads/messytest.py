import math
import os  # unused import ❶

x = 10
y = x + z   # z is undefined ❷

def add(a, b):
    result = a + b   # result unused ❸
    return a + b

def unused_function():   # unused function ❹
    print("I am never called")

name = "Eman"
name = "Eman Again"   # shadowed variable ❺

