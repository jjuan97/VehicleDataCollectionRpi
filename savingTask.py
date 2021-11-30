import sqlite3
import time
from apscheduler.schedulers.background import BackgroundScheduler

try:
  db_connection = sqlite3.connect('vehicledatabase.db')
  cursor = db_connection.cursor()
  cursor.execute('''CREATE TABLE IF NOT EXISTS vehicledata (
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
  cursor.close()
  db_connection.close()
except Error as e:
    print(e)

def slowTask():
  db_connection = sqlite3.connect('vehicledatabase.db')
  cursor = db_connection.cursor()
  data = [100, 'unVehiculo', 0.1, 0.2, time.time() ]
  print("Saving data at ", time.time())
  cursor.execute('''INSERT INTO vehicledata (
		idTrip,
		idVehicle,
		latitude,
		longitude,
		timestamp) 
		VALUES (?, ?, ?, ?, ?)''', data)
  db_connection.commit()
  cursor.close()
  db_connection.close()

scheduler = BackgroundScheduler(timezone="America/Bogota", job_defaults={'max_instances': 2})
scheduler.add_job(slowTask, 'interval', seconds=0.050)
scheduler.start()

try:
  # This is here to simulate application activity (which keeps the main thread alive).
  while True:
    time.sleep(2)
except (KeyboardInterrupt, SystemExit):
  # Not strictly necessary if daemonic mode is enabled but should be done if possible
  scheduler.shutdown()
