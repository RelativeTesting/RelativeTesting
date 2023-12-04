def test4():
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

    return x, y
