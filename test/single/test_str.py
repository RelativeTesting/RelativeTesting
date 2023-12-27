from symbolic.args import *
# @symbolic(param1 = "@(param1 >= 0) and (param2 >= 0)")
# def test_str(param1, param2):
#     color_chnl_byte = 3
#     modem_bandwidth = 64 * 10 ** 3
#     ethernet_bandwidth = 10 * 10 ** 6
#     seconds_in_hours = 3600
#     img_width = param1
#     img_height = param2
#     total_bytes = img_width * img_height * color_chnl_byte
#     total_bits = total_bytes * 8
#     modem_transmission_delay = total_bits / modem_bandwidth
#     ethernet_transmission_delay = total_bits / ethernet_bandwidth
#     modem_delay_hours = modem_transmission_delay // seconds_in_hours
#     modem_delay_minutes = (modem_transmission_delay - modem_delay_hours *
#          seconds_in_hours) // 60
#     model_delay_seconds = modem_transmission_delay % 60
#     ethernet_delay_hours = ethernet_transmission_delay // seconds_in_hours
#     ethernet_delay_minutes = (ethernet_transmission_delay - 
#          ethernet_delay_hours * seconds_in_hours) // 60
#     ethernet_delay_seconds = ethernet_transmission_delay % 60
    # print()
    # print('Tranmission delay of an ', img_width, 'x', img_height,
    #     ' image - (', total_bits, ' bits in total)', sep='')
    # print('Over 64 Kbps modem connection:', int(modem_delay_hours),
    #     'hour(s),', int(modem_delay_minutes), 'minute(s) and', format(
    #     model_delay_seconds, '.4f'), 'second(s)')
    # print('Over 10 Mbps ethernet connection:', int(ethernet_delay_hours),
    #     'hour(s),', int(ethernet_delay_minutes), 'minute(s) and', format(
    #     ethernet_delay_seconds, '.4f'), 'second(s)')


# @types(x="int", y = "int")
# @symbolic(x="@(x > 10 and x < 20) and ((x == 11) or (x == 18))")
# #@symbolic(x="@(x > y and y==6)")
# def test_str(x, y):
#     if x > 15:
#         return 1 
#     return 2

# # @symbolic(x = "@(x != 2) and (y > 2) ")
# def test_str(x,y):
#     b = 1
#     if x > 3:
#         if x % 5 == 1:
#             if x < 27:
#                 if x % 8 == 3:
#                     b = 2
#     return b
    

#@symbolic(x = "@(x != 2) and (y > 2) ")
# def test_str(x,y):
    
#     #a = x * 3
#     #c = (x * (y * 15)) % 40
#     for i in range(5 ):
#         x //= 3
#         if x < 3:
#             return 3


#     return 2

# def test_str(x,y):

#      # a = (x * y)
#      # b = a*12
#      c = (x * (y * 15)) % 40
#      return 2

# def test_str(x, y):
#     a = 1
#     if x > 5:
#         if y > 10:
#             a = 2
#     return a

# def test_str(x,y):
#     a = ((x*5)*4)+20

def test_str(x,y):
    a = 10 / x

    if y > 8:
        return 2
    return 1

def test():
    x = int(input())
    if x > 3:
        return 1
    return 2

