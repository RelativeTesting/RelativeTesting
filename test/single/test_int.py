from symbolic.args import *

@symbolic(x="@ x >=  y")
def test_int(x, y):
    if x == 1:
        return 1
    if y > 2:
        return 2
    return 3