from symbolic.args import *

@types(x="str", y="str")
def test_str(x, y, z):
    if x == "bbbb":
        return 1
    if y < "as":
        return 2
    if z == 5:
        return 3
    return 4