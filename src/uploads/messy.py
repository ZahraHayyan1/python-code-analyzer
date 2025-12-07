import math
import os

def badFunction(x,y,z):
    if x>10:
        if y>5:
            print("deep nesting")
    for i in range(10):
        print(i)

def unused_vars():
    a = 10
    b = 20
    return a

class Test:
    def method(self):
        x=10
        print(x)

