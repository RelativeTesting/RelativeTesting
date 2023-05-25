from symbolic.args import *

@types(x="int", y="int")
@symbolic(x="@ x != 0")
def test_int(x, y):
    if x == 3:
        return 1
    if y == 4:
        return 2
    return 3    