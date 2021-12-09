from flask import Flask, render_template, request
from flask_socketio import SocketIO
from apscheduler.schedulers.background import BackgroundScheduler
from multiprocessing import Process, Value, Array, Lock

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
recording_shared = Value('i', 0)
pos_s = Array('d', [1.0, 1.0])
position = [1.0, 1.0]
lock = Lock()

data_to_show = { "accX": 0, "accY": 0, "accZ": 0,
	"velAngX": 0, "velAngY": 0, "velAngZ": 0,
	"magX": 0, "magY": 0, "magZ": 0,
	"lat": 0, "lng": 0
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
	

def reading_gps_data (latitudeS, longitudeS, recordingS):
	while True:
		if (recordingS.value == 1):
			latitude, longitude = gps_module.readGPSPosition2()
			latitudeS.value = latitude
			longitudeS.value = longitude
			#print('lat: {} - lng: {}'.format(latitude,longitude))
		time.sleep(0.1)
		
def reading_gps_data2 (pos_s, l):
	while True:
		#l.acquire()
		latitude, longitude = gps_module.read_GPS_position3()
		if (latitude != -1):
			pos_s[0] = latitude
			pos_s[1] = longitude
			time.sleep(0.1)
		#print('lat: {} - lng: {}'.format(latitude,longitude))
		#l.release()


def saving_task (pos_s, l):
	"""Save all captured data
	This function captured and save data from all modules
	(IMU, GPS, OBD-II), the data is saved into database
	
	Keyword arguments:
	temp_data -- List with this variables [latitude, longitude, conditional]
	"""
	l.acquire()
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
	# latitude, longitude, cond = temp_data
	latitude, longitude = pos_s
	#print(latitude)
	
	# Insert data into database	
	data = [100, 'idV', time.time(), 
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
	l.release()
	
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
	global recording, pos_s, lock
	request_data = request.get_json()
	recording = request_data['recording']
	recording_shared.value = 1 if (recording) else 0
	idVehicle = request_data['idVehicle']
	freq = request_data['freq']

	response = 'Rpi is now {}'.format('recording' if (recording) else 'stopped')
	print(pos_s)

	if(recording):
		global firstRecording, scheduler
		
		scheduler.add_job(saving_task, args=[pos_s, lock], trigger='interval', seconds=0.05, id="saving_task")
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
	#threading.Thread(target=reading_gps_data, args=(temp_data,), daemon=True).start()
	
	p = Process(target=reading_gps_data2, args=(pos_s, lock,), daemon=True)
	p.start()
    
	socketio.run(app, debug=True, port=8080, host='0.0.0.0')
	# app.run(debug=True, port=80, host='0.0.0.0')
