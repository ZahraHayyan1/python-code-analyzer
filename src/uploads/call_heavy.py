def compute(x):
    return abs(x) + round(x) + int(x) + float(x)

def spam():
    print("Hello")
    print("Test")
    print("Again")

def chain():
    x = max(min(10, 5), abs(-3))
    y = sorted([3, 1, 2])
    z = sum([1, 2, 3])
    return x, y, z
