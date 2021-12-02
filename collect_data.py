import sqlite3
import time
from datetime import date
from imu import mpu6050
from gps import gps_module
from apscheduler.schedulers.background import BackgroundScheduler

scheduler = BackgroundScheduler(timezone="America/Bogota", job_defaults={'max_instances': 2})
db = './database/vehicledatabase.db'
temp_data = [0, 0, True]

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
	
@scheduler.scheduled_job('date', id="reading", args=[temp_data])
def reading_gps_data(temp_data):
	"""Read GPS Data
	Function to read GPS data from gps_module,
	the data from GPS latitude and longitude
	is saved in temp_data[0] and temp_data[1]
	
	Keyword arguments:
    temp_data -- List with this variables [latitude, longitude, conditional]
	"""
	while temp_data[2]:
		latitude, longitude = gps_module.readGPSPosition()
		temp_data[0] = latitude
		temp_data[1] = longitude
		print(temp_data)

@scheduler.scheduled_job('interval', seconds=0.050, id="saving", args=[temp_data])
def saving_task(temp_data):
	"""Save all captured data
	This function captured and save data from all modules
	(IMU, GPS, OBD-II), the data is saved into database
	
	Keyword arguments:
    temp_data -- List with this variables [latitude, longitude, conditional]
    """
	# Create connection
	db_connection = create_connection()
	cursor = db_connection.cursor()
	
	# Load Kinematic data
	kinematic_data = mpu6050.read_data()
	accX, accY, accZ = kinematic_data[0]
	velAngX, velAngY, velAngZ = kinematic_data[1]
	magX, magY, magZ = 0, 0, 0 #kinematic_data[2]
	
	# Load GPS data
	latitude, longitude, cond = temp_data
	
	# Insert data into database
	data = [100, str(cond), time.time(), 
			accX, accY, accZ, 
			velAngX, velAngY, velAngZ,
			magX, magY, magZ,
			latitude, longitude
			]
	#print("Saving data at: ", time.strftime('%Y-%m-%d %H:%M:%S',time.gmtime(time.time())))
	query = '''INSERT INTO vehicledata 
			(
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
				longitude
			)
			VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'''
	cursor.execute(query, data)
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
		
		print("Start")
		scheduler.start()
		time.sleep(5)
		
		print("Pause")
		temp_data[2] = False
		scheduler.pause()
		#scheduler.remove_all_jobs()
		time.sleep(5)
		
		print("Start again")
		temp_data[2] = True
		scheduler.resume()
		time.sleep(5)
		
		print("Shutdown")
		scheduler.shutdown(wait=False)
		while True:
			print("FINISHED")
			time.sleep(2)
	except (KeyboardInterrupt, SystemExit):
		# Not strictly necessary if daemonic mode is enabled but should be done if possible
		scheduler.shutdown(wait=False)
