color_chnl_byte = 3
modem_bandwidth = 64 * 10**3
ethernet_bandwidth = 10 * 10**6
seconds_in_hours = 3600

img_width = int(input("Please enter the image width in pixels: "))
img_height = int(input("Please enter the image height in pixels: "))

total_bytes = img_width * img_height * color_chnl_byte
total_bits = total_bytes * 8

modem_transmission_delay = total_bits / modem_bandwidth
ethernet_transmission_delay = total_bits / ethernet_bandwidth

modem_delay_hours = modem_transmission_delay // seconds_in_hours
modem_delay_minutes = (modem_transmission_delay - modem_delay_hours*seconds_in_hours) // 60
model_delay_seconds = modem_transmission_delay % 60

ethernet_delay_hours = ethernet_transmission_delay // seconds_in_hours
ethernet_delay_minutes = (ethernet_transmission_delay - ethernet_delay_hours*seconds_in_hours) // 60
ethernet_delay_seconds = ethernet_transmission_delay % 60

print()
print('Tranmission delay of an ', img_width, 'x', img_height,' image - (', total_bits, ' bits in total)', sep='')
print('Over 64 Kbps modem connection:', int(modem_delay_hours), 'hour(s),', int(modem_delay_minutes), 'minute(s) and', format(model_delay_seconds, '.4f'), 'second(s)')
print('Over 10 Mbps ethernet connection:', int(ethernet_delay_hours), 'hour(s),', int(ethernet_delay_minutes), 'minute(s) and', format(ethernet_delay_seconds, '.4f'), 'second(s)')