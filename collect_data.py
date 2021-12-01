import sqlite3
import time
from imu import mpu6050
from gps import gps_module
from apscheduler.schedulers.background import BackgroundScheduler

db = './database/vehicledatabase.db'
gps_data = [0, 0]

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
	
def reading_gps_data(gps_data):
	
	while True:
		latitude, longitude = gps_module.readGPSPosition()
		gps_data[0] = latitude
		gps_data[1] = longitude
		#print(gps_data)

def saving_task(gps_data):
	# Create connection
	db_connection = create_connection()
	cursor = db_connection.cursor()
	
	# Load Kinematic data
	kinematic_data = mpu6050.read_data()
	accX, accY, accZ = kinematic_data[0]
	velAngX, velAngY, velAngZ = kinematic_data[1]
	magX, magY, magZ = 0, 0, 0 #kinematic_data[2]
	
	# Load GPS data
	latitude, longitude = gps_data
	#print(latitude, longitude)
	
	# Insert data into database
	data = [100, 'unVehiculo', time.time(), 
		accX, accY, accZ, 
		velAngX, velAngY, velAngZ,
		magX, magY, magZ,
		latitude, longitude]
	print("Saving data at: ", time.strftime('%Y-%m-%d %H:%M:%S',time.gmtime(time.time())))
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
			VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', data)
	db_connection.commit()
	cursor.close()
	db_connection.close()

def main():
	print("Connecting to database ...")
	create_database()
	print("Connected!!")


if __name__ == "__main__":
	try:
		# This is here to simulate application activity (which keeps the main thread alive).
		main()
		scheduler = BackgroundScheduler(timezone="America/Bogota", job_defaults={'max_instances': 2})
		scheduler.add_job(reading_gps_data, args=[gps_data], id="reading")
		scheduler.add_job(saving_task, 'interval', args=[gps_data], seconds=0.050, id="saving")
		scheduler.start()
		for i in range(10):
			time.sleep(2)
		scheduler.shutdown()
		while True:
			print("FINISHED")
			time.sleep(2)
	except (KeyboardInterrupt, SystemExit):
		# Not strictly necessary if daemonic mode is enabled but should be done if possible
		scheduler.shutdown()
