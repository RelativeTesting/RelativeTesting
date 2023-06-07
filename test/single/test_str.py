from symbolic.args import *

@types(x="str", y="str")
def test_str(x, y):
    if x == "3":
        return 1
    if y != "4":
        return 2
    return 3