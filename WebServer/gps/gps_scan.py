import pynmea2
import serial
import sqlite3
import time

ser = serial.Serial('/dev/ttyS0', 9600, timeout=5.0)

# Gps frequency adjustment - once execution
'''
freq5Hz = b'\xB5\x62\x06\x08\x06\x00\xC8\x00\x01\x00\x01\x00\xDE\x6A'
freq1Hz = b'\xB5\x62\x06\x08\x06\x00\xE8\x03\x01\x00\x01\x00\x01\x39'
ser.write(freq5Hz)
s = ser.readline()
print(s)
'''

data_count = 0
while (1):
	try:
		line = ''.join(map(chr,ser.readline()))
		if line[0:6] == "$GPRMC":
			newmsg = pynmea2.parse(line)
			print(newmsg)
			lat = newmsg.latitude
			lng = newmsg.longitude
			gps = "Latitude=" + str(lat) + " and Longitude=" + str(lng)
			data_count += 1
			print("ID: {0} DATA: {1}".format(data_count, gps))
		else:
			print("NO GPRMC DATA")

	except (serial.SerialException) as e:
		print('Device error: {}'.format(e))
		break

	except (pynmea2.ParseError) as e:
		print('Parse error: {}'.format(e))
		continue
