import math
import os

class Calculator:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def add(self):
        return self.x + self.y

    def multiply(self):
        return self.x * self.y


def greet(name):
    print(f"Hello {name}")

def nested_example(n):
    for i in range(n):
        if i % 2 == 0:
            print("Even")
        else:
            print("Odd")

if __name__ == "__main__":
    c = Calculator(3, 5)
    print(c.add())
    print(c.multiply())

    greet("Iman")
    nested_example(5)
