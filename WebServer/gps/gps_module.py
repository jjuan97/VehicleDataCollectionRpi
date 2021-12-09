import pynmea2
import serial
import time
from multiprocessing import Process

ser = serial.Serial('/dev/ttyAMA0', 9600, timeout=0.02)
FREQ5HZ = b'\xB5\x62\x06\x08\x06\x00\xC8\x00\x01\x00\x01\x00\xDE\x6A'
FREQ1HZ = b'\xB5\x62\x06\x08\x06\x00\xE8\x03\x01\x00\x01\x00\x01\x39'
latitude = 1.0
longitude = 1.0

def configGPSRate(freq):
	if (freq == 5):
		ser.write(FREQ5HZ)
		return ser.readline()
	else:
		ser.write(FREQ1HZ)
		return ser.readline()

def readGPSPosition():	
	line = ''.join(map(chr, ser.readline()))
	while (line[0:6] != "$GPRMC"):
		line = ''.join(map(chr, ser.readline()))
	newmsg=pynmea2.parse(line)
	return newmsg.latitude, newmsg.longitude
	
def readGPSPosition2():	
	line = ''.join(map(chr, ser.readline()))
	while (line[0:6] != "$GPRMC"):
		line = ''.join(map(chr, ser.readline()))
		time.sleep(0.1)
	newmsg=pynmea2.parse(line)
	return newmsg.latitude, newmsg.longitude
			
def read_GPS_position3():	
	msg_type = ''.join(map(chr, ser.read(6)))
	if (msg_type != "$GPRMC"):
		ser.readline()
		return -1, -1
	else:
		msg = msg_type + ''.join( map(chr, ser.readline()) )		
		newmsg = pynmea2.parse(msg)
		#print('{} - lat: {}, lng:{}'.format(time.strftime('%H:%M:%S',time.gmtime(time.time())), newmsg.latitude, newmsg.longitude) )
		return newmsg.latitude, newmsg.longitude

def print_data(num: int = 10):
	"""Print GPS data
	
	Print GPS data capture for Neo6M module,
	this data is parsed from nemea code GPRMC
	
	Keyword arguments:
    num -- int that define loops for function (default 10)
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
			
def main():
	"""Terminal app
	Terminal app  to define the hertz for GPS and print data captured
	"""
	option = str(input("Desea configurar la frecuencia del GPS, S/N: ")).upper()
	if option == "S":
		freq= int(input("Digite la frecuencia deseada en Hz (Valores permitidos 1 y 5): "))
		while (freq != 1) and (freq != 5):
			freq = int(input("Valor de frecuencia no permitido!!\n"
							 + "Digite la frecuencia deseada en Hz (Valores permitidos 1 y 5): "))
		print("Frecuencia establecida en {} Hz".format(freq))
		print("Serial response: ", configGPSRate(freq))
		
	elif option == "N":
		print("Mostrando datos GPS:")
		print_data()
		
	else:
		print("Opción invalida")


if __name__ == "__main__":
	main()
