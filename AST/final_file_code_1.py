def my_function(param1: int, param2: int, param3: int, param4: int):
    take_off_distance = 300
    flight_distance = 384400
    landing_distance = 100
    take_off_v = int(param1)
    flight_v = int(param2)
    landing_v = int(param3)
    lower = int(param4.toLower())
    t1 = take_off_distance * 1000 / take_off_v
    t2 = flight_distance * 1000 / flight_v
    t3 = landing_distance * 1000 / landing_v
    total_secs = t1 + t2 + t3
    days = total_secs // (24 * 60 * 60)
    total_secs %= 24 * 60 * 60
    hours = total_secs // (60 * 60)
    total_secs %= 60 * 60
    minutes = total_secs // 60
    seconds = total_secs % 60
    print('The mission will take', format(days, '.0f'), 'day(s),', format(
        hours, '.0f'), 'hour(s),', format(minutes, '.0f'), 'minute(s),',
        format(seconds, '.2f'), 'second(s).')
