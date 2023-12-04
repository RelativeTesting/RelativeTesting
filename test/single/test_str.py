from symbolic.args import *

@types(x="int", y = "int")
@symbolic(x="@(x > 10 and x < 20) and ((x == 11) or (x == 18))")
#@symbolic(x="@(x > y and y==6)")
def test_str(x, y):
    if x > 15:
        return 1 
    return 2

    
