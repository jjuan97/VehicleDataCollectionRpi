import sqlite3
import time

try:
	con = sqlite3.connect('vehicledatabase.db')
except Error as e:
	print(e)

cur = con.cursor()

cur.execute('''CREATE TABLE IF NOT EXISTS vehicledata (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		idTrip INTEGER,
		idVehicle TEXT,
		timestamp DATETIME,
		speed NUMBER,
		accX NUMBER,
		accY NUMBER,
		accZ NUMBER,
		velAngX NUMBER,
		velAngY NUMBER,
		velAngZ NUMBER,
		magX NUMBER,
		magY NUMBER,
		magZ NUMBER,
		latitude NUMBER,
		longitude NUMBER,
		breakPosition NUMBER,
		eventClass BOOLEAN)''')

for i in range(1, 10):
	data = [i, 'unVehiculo', 0.1, 0.2, time.time() ]
	cur.execute('''INSERT INTO vehicledata (
			idTrip,
			idVehicle,
			latitude,
			longitude,
			timestamp) 
			VALUES (?, ?, ?, ?, ?)''', data )
	con.commit()
con.close()


