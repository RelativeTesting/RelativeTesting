from symbolic.args import *


@symbolic(param1!=0, param2!=0, param3!=0)

["!=", 0, param1]
def power(param1, param2, param3):
	take_off_distance = 300 #km
	flight_distance = 384400 #km
	landing_distance = 100 #km
	
	if param1 == 0 or param2 == 0 or param3 == 0:
		return 2

	take_off_v = int(param1) #m/s
	flight_v = int(param2) #m/s
	landing_v = int(param3) #m/s
	
	t1 = take_off_distance*1000 / param1
	t2 = flight_distance*1000 / param2
	t3 = landing_distance*1000 / param3
	
	total_secs = t1+t2+t3
	#print("Total_secs:", total_secs)
	
	days = total_secs // (24 * 60 * 60)
	total_secs %= (24 * 60 * 60)
	
	hours = total_secs // (60 * 60)
	total_secs %= (60 * 60)
	
	minutes = total_secs // 60
	seconds = total_secs % 60
	
	print("The mission will take", format(days,".0f"),"day(s),", format(hours,".0f"), "hour(s),", format(minutes,".0f"), "minute(s)," , format(seconds,".2f"), "second(s).")

	return 1
def expected_result():
	return [1,2]

