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
db_temp = './database/locationdatabase.db'

recording = False
firstRecording = True
id_vehicle = Array('u', list('defaultID'))
period = Value('d', 20)
time_elapsed = Value('d', 0)

connection_db = None
cursor_db = None
writer = sqlite3.connect(db_temp, isolation_level=None)
writer.execute('pragma journal_mode=wal;')
reader = sqlite3.connect(db_temp, isolation_level=None)
reader.execute('pragma journal_mode=wal;')

data_to_show = { "accX": 0, "accY": 0, "accZ": 0,
	"velAngX": 0, "velAngY": 0, "velAngZ": 0,
	"magX": 0, "magY": 0, "magZ": 0,
	"lat": 0, "lng": 0
	}


def create_connection():
	"""Database connection
	"""
	try:
		conn = sqlite3.connect(db, isolation_level=None)
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
	
	with open('./database/configDB_temp.sql', 'r') as sql_file:
		sql_script = sql_file.read()	
	writer.executescript(sql_script)
		

def reading_gps_data (writer):
	while True:
		latitude, longitude = gps_module.read_GPS_position()
		writer.execute('''UPDATE gpslocation
			SET id = 0, latitude = ?, longitude = ?
			WHERE id=0''', [latitude,longitude] )		
		#print('lat: {} - lng: {}'.format(latitude, longitude))


def saving_task (conn, cursor, reader, id_vehicle, t):
	
	"""Save all captured data
	This function captured and save data from all modules
	(IMU, GPS, OBD-II), the data is saved into database
	
	Keyword arguments:
	temp_data -- List with this variables [latitude, longitude, conditional]
	"""

	# Load Kinematic data
	kinematic_data = mpu6050.read_data()
	accX, accY, accZ = kinematic_data[0]
	velAngX, velAngY, velAngZ = kinematic_data[1]
	magX, magY, magZ = 0, 0, 0 #kinematic_data[2]
	
	# Load GPS data
	latitude = 0
	longitude = 0
	for row in reader.execute('SELECT * FROM gpslocation WHERE id=0'):
		latitude = row[1]
		longitude = row[2]
	print('lat: {} - lng: {}'.format(latitude, longitude))
	
	# Insert data into database	
	data = [100, "".join(id_vehicle.value), time.time(), 
			accX, accY, accZ, 
			velAngX, velAngY, velAngZ,
			magX, magY, magZ,
			latitude, longitude
			]
	print("Saving data at: ", time.strftime('%H:%M:%S',time.gmtime(time.time())))
	
	query = '''INSERT INTO vehicledata
			(
				idTrip, idVehicle, timestamp, 
				accX, accY,	accZ,
				velAngX, velAngY, velAngZ,
				magX, magY,	magZ,
				latitude, longitude
			)
			VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'''
	
	cursor.execute(query, data)
	
	if ((time.time()-t.value) > 0.2 ):
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
		send_data(data_to_show)
		t.value = time.time()
		

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
	global recording, connection_db, cursor_db, id_vehicle, period, time_elapsed
	request_data = request.get_json()
	recording = request_data['recording']
	id_vehicle.value = list(request_data['idVehicle'])
	period.value = 1/int(request_data['freq'])

	response = 'Rpi is now {}'.format('recording' if (recording) else 'stopped')

	if(recording):
		global firstRecording, scheduler, reader
		
		connection_db = create_connection()
		cursor_db = connection_db.cursor()
		
		time_elapsed.value = time.time()
		scheduler.add_job(saving_task, 
			args=[connection_db, cursor_db, reader, id_vehicle, time_elapsed],
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
		p = Process(target=reading_gps_data, args=(writer,), daemon=True)
		p.start()
		socketio.run(app, debug=True, port=8080, host='0.0.0.0')
		# app.run(debug=True, port=80, host='0.0.0.0
		
	except KeyboardInterrupt:
		p.close()
