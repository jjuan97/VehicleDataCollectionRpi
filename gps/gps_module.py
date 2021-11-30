import pynmea2
import serial
import sqlite3
import time

ser = serial.Serial('/dev/ttyAMA0', 9600, timeout=5.0)
FREQ5HZ = b'\xB5\x62\x06\x08\x06\x00\xC8\x00\x01\x00\x01\x00\xDE\x6A'
FREQ1HZ = b'\xB5\x62\x06\x08\x06\x00\xE8\x03\x01\x00\x01\x00\x01\x39'

def configGPSRate(freq):
	if (freq == '5Hz'):
		ser.write(FREQ5HZ)
		return ser.readline()
	else:
		ser.write(FREQ1HZ)
		return ser.readline()
	

def readGPSPosition():	
	line = ''.join(chr(i) for i in ser.readline())
	while (line[0:6] != "$GPRMC"):
		line = ''.join(chr(i) for i in ser.readline())
	newmsg=pynmea2.parse(line)
	return newmsg.latitude, newmsg.longitude


def print_data(num: int = 10):
	"""
	Print GPS data for nmea code GPRMC
	
	Parameters: num -> int that define loops for function
	"""
	data_count = 0
	for i in range(0, num):
		try:
			lat, lng = readGPSPosition()
			gps = "Latitude=" + str(lat) + " and Longitude=" + str(lng)
			data_count += 1
			print("ID: {0} DATA: {1}".format(data_count, gps))

		except (serial.SerialException) as e:
			print('Device error: {}'.format(e))
			break

		except (pynmea2.ParseError) as e:
			print('Parse error: {}'.format(e))
			continue

if __name__ == "__main__":
	help(print_data.__doc__)
	
else:
	# wait for call functions from main module
	ser = serial.Serial('/dev/ttyAMA0', 9600, timeout=5.0)
	

	
