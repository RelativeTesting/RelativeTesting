def string_code(x,param1, param2, param3, param4, param5, param6, param7,
    param8, param9, param10, param11, param12):
    if x < 10:
        y = param1
        j = 0
        if j < y:
            x += param2
            j += 1
            if j < y:
                x += param3
                j += 1
                if j < y:
                    x += param4
                    j += 1
        assert j < y
        if x < 10:
            y = param5
            j = 0
            if j < y:
                x += param6
                j += 1
                if j < y:
                    x += param7
                    j += 1
                    if j < y:
                        x += param8
                        j += 1
            assert j < y
            if x < 10:
                y = param9
                j = 0
                if j < y:
                    x += param10
                    j += 1
                    if j < y:
                        x += param11
                        j += 1
                        if j < y:
                            x += param12
                            j += 1
                assert j < y
    assert x < 10