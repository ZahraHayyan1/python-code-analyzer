def compute(values):
    total = 0
    for v in values:
        if v > 10:
            total += v * 2
        else:
            if v % 2 == 0:
                total += v
            else:
                for i in range(v):
                    total += i
    return total
