def check(x):
    if x > 5:
        for i in range(x):
            if i % 2 == 0:
                while x > 0:
                    try:
                        if x == 3:
                            x -= 1
                        else:
                            x -= 2
                    except:
                        x -= 1
    return x
