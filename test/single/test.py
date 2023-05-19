from symbolic.args import *

@symbolic(x="@ x > y",y = "@ y > 6")
def test(x, y):
    if x == 3:
        return 1
    if y == 4:
        return 2
    return 3