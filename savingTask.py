import sqlite3
import time
from imu import mpu6050
from apscheduler.schedulers.background import BackgroundScheduler

db = './database/vehicledatabase.db'

def create_connection():
  """Database connection
  """
  try:
    conn = sqlite3.connect(db)
  except Error as e:
    print(e)
  return conn
  
def create_database():
  """Database creation
  """
  with open('./database/configDB.sql', 'r') as sql_file:
    sql_script = sql_file.read()

  db_connection = create_connection()
  cursor = db_connection.cursor()
  cursor.executescript(sql_script)
  db_connection.commit()
  cursor.close()
  db_connection.close()

def slowTask():
  # Create connection
  db_connection = create_connection()
  cursor = db_connection.cursor()
  
  # Load Kinematic data
  kinematic_data = mpu6050.read_data()
  accX, accY, accZ = kinematic_data[0]
  velAngX, velAngY, velAngZ = kinematic_data[1]
  magX, magY, magZ = 0, 0, 0 #kinematic_data[2]
  
  # Load GPS data
  cursor.execute('''SELECT latitude, longitude FROM gpsTempData''')
  latitude, longitude = cursor.fetchone()
  
  # Insert data into database
  data = [100, 'unVehiculo', time.time(), 
	  accX, accY, accZ, 
	  velAngX, velAngY, velAngZ,
	  magX, magY, magZ,
	  latitude, longitude]
  print("Saving data at ", time.time())
  cursor.execute('''INSERT INTO vehicledata (
		idTrip,
		idVehicle,
		timestamp,
		accX,
		accY,
		accZ,
		velAngX,
		velAngY,
		velAngZ,
		magX,
		magY,
		magZ,
		latitude,
		longitude)
		VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', data)
  db_connection.commit()
  cursor.close()
  db_connection.close()

def main():
  create_database()
  
  scheduler = BackgroundScheduler(timezone="America/Bogota", job_defaults={'max_instances': 2})
  scheduler.add_job(slowTask, 'interval', seconds=0.050)
  scheduler.start()

main()

try:
  # This is here to simulate application activity (which keeps the main thread alive).
  while True:
    time.sleep(2)
except (KeyboardInterrupt, SystemExit):
  # Not strictly necessary if daemonic mode is enabled but should be done if possible
  scheduler.shutdown()
