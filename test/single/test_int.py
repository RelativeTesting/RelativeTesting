from symbolic.args import *

@types(x="str", y="str")
def test_int(x, y, z):
     


    if x == "bbbb":
        return 1


    if y < "fffff":
        return 2

    if len(x) < 8:
        return 5
    if z == 5:
        return 3
    
    # if len(y) >= 2:
    #     if y[0] == 'a':
    #         return 4

   
    return 6


    

# def test_int(x, y, z):
#     if y == 3:
#         return 1
#     if x < 6:
#         return 2
#     if z == 5:
#         return 4
#     return 3