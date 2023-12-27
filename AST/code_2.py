letters = "abcdefgh"

knight_hor = input("Please enter horizontal position of the knight (a,b,c,d,e,f,g,h): ").lower()
i=0
while i<10:
  x=int(input("Please enter integer something:"))
  i+=1
if len(knight_hor)!=1 or not knight_hor.isalpha(): 
  print("Horizontal input for knight is not a letter")
elif knight_hor not in letters:
  print("Horizontal input for knight is not a proper letter")
else:
  knight_column = input("Please enter vertical position of the knight (1,2,3,4,5,6,7,8): ")
  if not knight_column.isdigit():
    print("Vertical input for knight is not a number")
  else:
    knight_column = int(knight_column)
    if knight_column < 1 or knight_column > 8:
      print("Vertical input for knight is not a proper number")
    else:
      bishop_hor = input("Please enter horizontal position of the bishop (a,b,c,d,e,f,g,h): ").lower()
      if len(bishop_hor)!=1 or not bishop_hor.isalpha():
        print("Horizontal input for bishop is not a letter")
      elif bishop_hor not in letters:
        print("Horizontal input for bishop is not a proper letter")
      else:
        bishop_column = input("Please enter vertical position of the bishop (1,2,3,4,5,6,7,8): ")
        if not bishop_column.isdigit():
          print("Vertical input for bishop is not a number")    
        else:
          bishop_column = int(bishop_column)
          if bishop_column < 1 or bishop_column > 8:
            print("Vertical input for bishop is not a proper number")
          else:
            row_dif = abs(letters.index(knight_hor) - letters.index(bishop_hor))
            hor_dif = abs(knight_column - bishop_column)
            if row_dif == 0 and hor_dif == 0:
              print("They can't be in the same square")
            elif row_dif != 0 and hor_dif != 0 and row_dif+hor_dif == 3:
              print("Knight can attack bishop")
            elif row_dif == hor_dif:
              print("Bishop can attack knight")
            else:
              print("Neither of them can attack each other")