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

from imu import mpu6050
from gps import gps_module

eventlet.monkey_patch(thread=True, time=True)
app = Flask(__name__)
socketio = SocketIO(app)
scheduler = BackgroundScheduler(timezone="America/Bogota", job_defaults={'max_instances': 4})

db = './database/vehicledatabase.db'
recording = False
firstRecording = True
lat = Value('d', 1.0)
lng = Value('d', 1.0)
count = Value('i', 0)
id_vehicle = Array('u', list('defaultID'))
period = Value('d', 20)
time_elapsed = Value('d', 0)
lock = Lock()

connection_db = None
cursor_db = None

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
		
def reading_gps_data (lat, lng, l):
	while True:
		latitude, longitude = gps_module.read_GPS_position()
		lat.value = latitude
		lng.value = longitude
		#print('lat: {} - lng: {}'.format(lat.value, lng.value))
		'''
		latitude, longitude = gps_module.read_GPS_position_2()
		if (latitude != -1):
			lat.value = latitude
			lng.value = longitude
			print('lat: {} - lng: {}'.format(longitude, longitude))
		time.sleep(0.1)	
		'''

def saving_task (lat, lng, conn, cursor, count, l, id_vehicle, t):
	"""Save all captured data
	This function captured and save data from all modules
	(IMU, GPS, OBD-II), the data is saved into database
	
	Keyword arguments:
	temp_data -- List with this variables [latitude, longitude, conditional]
	"""
	#l.acquire()
	# Load Kinematic data
	kinematic_data = mpu6050.read_data()
	accX, accY, accZ = kinematic_data[0]
	velAngX, velAngY, velAngZ = kinematic_data[1]
	magX, magY, magZ = 0, 0, 0 #kinematic_data[2]
	
	# Load GPS data
	# lat and lng contains the position 
	
	# Insert data into database	
	data = [100, "".join(id_vehicle.value), time.time(), 
			accX, accY, accZ, 
			velAngX, velAngY, velAngZ,
			magX, magY, magZ,
			lat.value, lng.value
			]
	print("Saving data at: ", time.strftime('%H:%M:%S',time.gmtime(time.time())))
	
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
	
	if ((time.time()-t.value) > 0.2 ):
		print('lat: {} - lng: {}'.format(lat.value, lng.value))
		data_to_show["accX"]= accX
		data_to_show["accY"]= accY
		data_to_show["accZ"]= accZ
		data_to_show["velAngX"]= velAngX
		data_to_show["velAngY"]= velAngY
		data_to_show["velAngZ"]= velAngZ
		data_to_show["magX"]= 0
		data_to_show["magY"]= 0
		data_to_show["magZ"]= 0
		data_to_show["lat"]= lat.value
		data_to_show["lng"]= lng.value
		send_data(data_to_show)
		t.value = time.time()
		
	#l.release()


def send_data(data_to_show):
	socketio.emit('vehicleData', json.dumps(data_to_show))
    

@app.route('/')
def index():
	current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

	templateData = {
		'title' : 'Vehicle data Recording'
	}
	return render_template('index.html', **templateData)


@app.route('/recordingTask', methods=['POST'])
def handleRecordingTask():
	global recording, lat, lng, connection_db, cursor_db, count, lock, id_vehicle, period, time_elapsed
	request_data = request.get_json()
	recording = request_data['recording']
	id_vehicle.value = list(request_data['idVehicle'])
	period.value = 1/int(request_data['freq'])

	response = 'Rpi is now {}'.format('recording' if (recording) else 'stopped')

	if(recording):
		global firstRecording, scheduler
		
		connection_db = create_connection()
		cursor_db = connection_db.cursor()
		
		time_elapsed.value = time.time()
		scheduler.add_job(saving_task, 
			args=[lat,lng,connection_db,cursor_db,count,lock,id_vehicle,time_elapsed],
			trigger='interval', seconds=period.value, id="saving_task")
		
		if (firstRecording):
			scheduler.start()
			firstRecording = False
		else:
			scheduler.resume()
	else:
		scheduler.pause()
		scheduler.remove_all_jobs()
		connection_db.commit()
		cursor_db.close()
		connection_db.close()
	
	socketio.emit('vehicleDataConnect', json.dumps({"response": response}))
	return {"response": response}


@socketio.on('vehicleDataConnect')
def handle_connection(data):
	print('Incomming message: ' + data['data'])
	socketio.emit('vehicleDataConnect', json.dumps({"msg": "hola"}))


if __name__ == '__main__':
	try:
		create_database()
		p = Process(target=reading_gps_data, args=(lat,lng,lock))
		p.start()
		socketio.run(app, debug=True, port=8080, host='0.0.0.0')
		# app.run(debug=True, port=80, host='0.0.0.0')
	except KeyboardInterrupt:
		p.close()
