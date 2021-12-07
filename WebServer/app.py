from flask import Flask, render_template, request
from flask_socketio import SocketIO
from apscheduler.schedulers.background import BackgroundScheduler

import sqlite3
import eventlet
import datetime
import json
import random
import time
import threading

from imu import mpu6050
from gps import gps_module

eventlet.monkey_patch(thread=True, time=True)
app = Flask(__name__)
socketio = SocketIO(app)
scheduler = BackgroundScheduler(timezone="America/Bogota", job_defaults={'max_instances': 2})

db = './database/vehicledatabase.db'
recording = False
firstRecording = True
temp_data = [1, 1, False]
data_to_show = {
	"accX": 0,
	"accY": 0,
	"accZ": 0,
	"velAngX": 0,
	"velAngY": 0,
	"velAngZ": 0,
	"magX": 0,
	"magY": 0,
	"magZ": 0,
	"lat": 0,
	"lng": 0
}

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
	

def reading_gps_data (temp_data):
	while True:
		if (temp_data[2] == True):
			latitude, longitude = gps_module.readGPSPosition2()
			temp_data[0] = latitude
			temp_data[1] = longitude
			print(temp_data)
		time.sleep(0.1)


def saving_task (temp_data):
	"""Save all captured data
	This function captured and save data from all modules
	(IMU, GPS, OBD-II), the data is saved into database
	
	Keyword arguments:
	temp_data -- List with this variables [latitude, longitude, conditional]
	"""
	# Create connection	
	db = './database/vehicledatabase.db'
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
	print("Saving data at: ", time.strftime('%Y-%m-%d %H:%M:%S',time.gmtime(time.time())))
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
	
	data_to_show["accX"]= accX
	data_to_show["accY"]= accY
	data_to_show["accZ"]= accZ
	data_to_show["velAngX"]= velAngX
	data_to_show["velAngY"]= velAngY
	data_to_show["velAngZ"]= velAngZ
	data_to_show["magX"]= 0
	data_to_show["magY"]= 0
	data_to_show["magZ"]= 0
	data_to_show["lat"]= latitude
	data_to_show["lng"]= longitude
	
'''def send_data(data_to_show):
	socketio.emit('vehicleData', json.dumps(data_to_show))'''
    
@app.route('/')
def index():
	current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

	templateData = {
		'title' : 'Vehicle data Recording'
	}
	return render_template('index.html', **templateData)


@app.route('/recordingTask', methods=['POST'])
def handleRecordingTask():
	global recording
	request_data = request.get_json()
	recording = request_data['recording']
	temp_data[2] = recording
	idVehicle = request_data['idVehicle']
	freq = request_data['freq']

	response = 'Rpi is now {}'.format('recording' if (recording) else 'stopped')
	
	if(recording):
		global firstRecording, scheduler
		
		scheduler.add_job(saving_task, args=[temp_data], trigger='interval', seconds=0.05, id="saving_task")
		#scheduler.add_job(send_data, args=[data_to_show], trigger='interval', seconds=1, id="sending_task")
		#scheduler.add_job(reading_gps_data, args=[temp_data], trigger='date', id="read_gps_data")
		if (firstRecording):
			scheduler.start()
			firstRecording = False
		else:
			scheduler.resume()
	else:
		scheduler.pause()
		scheduler.remove_all_jobs()
	
	socketio.emit('vehicleDataConnect', json.dumps({"response": response}))
	return {"response": response}


@socketio.on('vehicleDataConnect')
def handle_connection(data):
	print('Incomming message: ' + data['data'])
	socketio.emit('vehicleDataConnect', json.dumps({"msg": "hola"}))

if __name__ == '__main__':
	create_database()
	threading.Thread(target=reading_gps_data, args=(temp_data,), daemon=True).start()
	socketio.run(app, debug=True, port=8080, host='0.0.0.0')
	# app.run(debug=True, port=80, host='0.0.0.0')
