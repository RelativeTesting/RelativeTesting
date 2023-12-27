from symbolic.args import * 
@types(param1="int", param2="int", param3="int")
@symbolic(param1="@param1 >= 100 and param1 <= 200", param2="@param2 > 100", param3="@param3 > 0 and param3 < 10000")
def power(param1, param2, param3):
	take_off_distance = 300 #km
	flight_distance = 384400 #km
	landing_distance = 100 #km

	take_off_v = param1 #m/s
	flight_v = param2 #m/s
	landing_v = param3 #m/s
	
	t1 = take_off_distance*1000 / take_off_v
	t2 = flight_distance*1000 / flight_v
	t3 = landing_distance*1000 / landing_v
	
	total_secs = t1+t2+t3
	
	days = total_secs // (24 * 60 * 60)
	total_secs %= (24 * 60 * 60)
	
	hours = total_secs // (60 * 60)
	total_secs %= (60 * 60)
	
	minutes = total_secs // 60
	seconds = total_secs % 60
	
	print("The mission will take", format(days,".0f"),"day(s),", format(hours,".0f"), "hour(s),", format(minutes,".0f"), "minute(s)," , format(seconds,".2f"), "second(s).")

	return 1