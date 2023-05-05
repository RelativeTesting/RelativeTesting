from symbolic.args import *

@symbolic(x="@ x>2", y="@ y<-3")
def test(x, y):
    if x > 3:
        return 1
    
    if y > 5:
        return x
    return 3