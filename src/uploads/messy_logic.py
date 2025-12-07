def process(values):
    result = []
    for v in values:
        if v % 2 == 0:
            if v > 10:
                if v < 100:
                    result.append(v * 2)
                else:
                    result.append(v - 1)
            else:
                if v == 4:
                    result.append(0)
                else:
                    result.append(v + 3)
        else:
            if v % 3 == 0:
                result.append(v * 5)
            else:
                for i in range(v):
                    if i % 2 == 0:
                        result.append(i)
    return result
