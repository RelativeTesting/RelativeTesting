def test3():
    x = 0
    y = 0

    while x < 10:
        x += 1
        y += 1
        print(x, y)
        for i in range(10):
            y += 1
        print(y)
    
    y = 0

    for i in range(6):
        y += 1
        print(y)
        for i in range(10):
            y += 1
        print(y)
    
    for i in range(10):
        y += 1
        print(y)

    return x, y
