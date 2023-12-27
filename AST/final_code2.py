def final_code(param1, param2, param3, param4, param5, param6, param7):
    letters = 'abcdefgh'
    knight_hor = param1.lower()
    i = 0
    if i < 10:
        x = param2
        i += 1
        if i < 10:
            x = param3
            i += 1
            if i < 10:
                x = param4
                i += 1
    assert i < 10
    if len(knight_hor) != 1 or not knight_hor.isalpha():
        print('Horizontal input for knight is not a letter')
    elif knight_hor not in letters:
        print('Horizontal input for knight is not a proper letter')
    else:
        knight_column = param5
        if not knight_column.isdigit():
            print('Vertical input for knight is not a number')
        else:
            knight_column = knight_column
            if knight_column < 1 or knight_column > 8:
                print('Vertical input for knight is not a proper number')
            else:
                bishop_hor = param6.lower()
                if len(bishop_hor) != 1 or not bishop_hor.isalpha():
                    print('Horizontal input for bishop is not a letter')
                elif bishop_hor not in letters:
                    print('Horizontal input for bishop is not a proper letter')
                else:
                    bishop_column = param7
                    if not bishop_column.isdigit():
                        print('Vertical input for bishop is not a number')
                    else:
                        bishop_column = bishop_column
                        if bishop_column < 1 or bishop_column > 8:
                            print(
                                'Vertical input for bishop is not a proper number'
                                )
                        else:
                            row_dif = abs(letters.index(knight_hor) -
                                letters.index(bishop_hor))
                            hor_dif = abs(knight_column - bishop_column)
                            if row_dif == 0 and hor_dif == 0:
                                print("They can't be in the same square")
                            elif row_dif != 0 and hor_dif != 0 and row_dif + hor_dif == 3:
                                print('Knight can attack bishop')
                            elif row_dif == hor_dif:
                                print('Bishop can attack knight')
                            else:
                                print('Neither of them can attack each other')
