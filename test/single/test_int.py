from symbolic.args import *

@types(x="str", y="str")
@symbolic(x = "@x > 'a'", z = "@z != 4", y = "@len(y) > 2 and y[1] == 'a'",)
def test_int(x, y, z):

    if (z > 3 and z < 10):
        if x == "araba":
            return 1
        else:
            return 2
    # if x == "bbbb":
    #     return 1

    # if y < "ddas":
    #     return 2

    # if x + y == "araba":
    #     return 9 
    
    # if len(y) > 2:
    #     if y[2] == 'a':
    #         return 4

    # if len(y) > 5:
    #      if y[2:4] == 'ca':
    #          return 10     
    #     return 7

    return 6


    

# def test_int(x, y, z):
#     if y == 3:
#         return 1
#     if x < 6:
#         return 2
#     if z == 5:
#         return 4
#     return 3


"""
TODO:
String Methodlari eklenecek / 1 hafta

If time permits
    float, boolean types

DONE:
Pre Assertionlar dynamic hale getirelecek / 2-3 Hafta 
Loop repeating parameters:
    Loop içerisinde dönen parametreler için değişecebilecek inputlar yaratmak.
Web Interface Yapilacak / 2 hafta
"""

