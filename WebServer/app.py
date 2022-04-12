from turtle import delay
from flask import Flask, render_template, request
from flask_socketio import SocketIO
from flask import g

from apscheduler.schedulers.background import BackgroundScheduler
from multiprocessing import Process, Value, Array, Lock

import sqlite3
import eventlet
import datetime
import json
import random
import time
import sqlite3
import firebase_admin

# Modules for variable detection
#from imu import mpu6050 # If use mpu6050
from imu import mpu9250_module
from gps import gps_module
from obd_2 import obd_module
from gpiozero import Button # Button to detect near-crash

# Firebase functionalities
from firebase_admin import credentials
from firebase_admin import db


# Firebase configuration
cred = credentials.Certificate("../vehicledatacollected-firebase-adminsdk-dfzqq-f41fc7bb31.json")
firebase_admin.initialize_app(cred, {
	'databaseURL': 'https://vehicledatacollected-default-rtdb.firebaseio.com'
})
ref = db.reference('/')

# Scheduler and Web Socket configuration
eventlet.monkey_patch(thread=True, time=True)
app = Flask(__name__)
socketio = SocketIO(app)
scheduler = BackgroundScheduler(timezone="America/Bogota", job_defaults={'max_instances': 4})

# Database names
LOCAL_DB = './database/vehicledatabase.db'
TEMPORAL_LOCATION_DB = './database/templocation.db'
TEMPORAL_OBD_DB = './database/tempobd.db'

# Variables
recording = False
firstRecording = True
id_vehicle = Array('u', list('defaultID'))
route = Array('u', list('defaultID'))
period = Value('d', 20)
time_elapsed = Value('d', 0)
trip_id = Value('i', -1)

# Config wal mode in temporal databases
connection_db = None
cursor_db = None
writer = sqlite3.connect(TEMPORAL_LOCATION_DB, isolation_level=None)
writer.execute('pragma journal_mode=wal;')
reader = sqlite3.connect(TEMPORAL_LOCATION_DB, isolation_level=None)
reader.execute('pragma journal_mode=wal;')

obd_writer = sqlite3.connect(TEMPORAL_OBD_DB, isolation_level=None)
obd_writer.execute('pragma journal_mode=wal;')
obd_reader = sqlite3.connect(TEMPORAL_OBD_DB, isolation_level=None)
obd_reader.execute('pragma journal_mode=wal;')

# Data to show in web socket functions
data_to_show = { "accX": 0, "accY": 0, "accZ": 0,
	"velAngX": 0, "velAngY": 0, "velAngZ": 0,
	"magX": 0, "magY": 0, "magZ": 0,
	"lat": 0, "lng": 0,"speed": 0, "accPosition": 0
	}
	
# Define the GPIO Settings in raspberry
button = Button(26) # GPIO where button is connected

# DB functions (create, connect, close, get, execute_query)
def create_connection():
	"""Start database connection
	"""
	try:
		conn = sqlite3.connect(LOCAL_DB)
	except Error as e:
		print(e)
	return conn

def create_databases():
	"""Databases creation

	Build a database from a sql file configuration
	"""
	with open('./database/configVehicleDB.sql', 'r') as sql_file:
		sql_script = sql_file.read()

	db_connection = create_connection()
	cursor = db_connection.cursor()
	cursor.executescript(sql_script)
	db_connection.commit()
	cursor.close()
	db_connection.close()
	
	with open('./database/configTempLocationDB.sql', 'r') as templocation_sql_file:
		templocation_sql_script = templocation_sql_file.read()
	writer.executescript(templocation_sql_script)

	with open('./database/configTempOBD.sql', 'r') as temp_obd_sql_file:
		temp_obd_sql_script = temp_obd_sql_file.read()
	obd_writer.executescript(temp_obd_sql_script)

def sqlite_dict(cursor, row):
	"""Row factory method

	It is executed for every result returned from the database to convert the result.
	For instance, in order to get dictionaries instead of tuples

	Returns:
		dict: A dictionary for this database connection
	"""
	return dict((cursor.description[idx][0], value)
				for idx, value in enumerate(row))

def get_db():
	"""Get database connection
	"""
	db_conn = getattr(g, '_database', None)
	if db_conn is None:
		db_conn = g._database = sqlite3.connect(LOCAL_DB)
	db_conn.row_factory = sqlite_dict
	return db_conn

@app.teardown_appcontext
def close_connection(exception):
	"""Close database connection

	Whenever the context is destroyed the database connection will be terminated.
	"""
	db_conn = getattr(g, '_database', None)
	if db_conn is not None:
		db_conn.close()

def get_data(query, args=(), one=False):
	"""Get data from database with a sql query

	Args:
		query (str): A SELECT sql query
		args (tuple, optional): Defaults to ().
		one (bool, optional): Define if only want a single result. Defaults to False.

	Returns:
		dict: rows of a query result
	"""
	cur = get_db().execute(query, args)
	rv = cur.fetchall()
	cur.close()
	return (rv[0] if rv else None) if one else rv

def execute_query(query):
	"""Execute a specific sql query

	Only queries without return.

	Args:
		query (str): A INSERT, UPDATE or DELETE sql query
	"""
	conn = get_db()
	cur = conn.cursor()
	cur.execute(query)
	cur.close()
	conn.commit()

# Multiprocess functions
def reading_gps_data (writer):
	"""Fuunction to manage gps data in a multiprocesing thread
	
	First read the actual gps data, then save this in TEMPORAL_LOCATION_DB

	Args:
		writer (sqlite3.Connection): A sqlite3 connection in wal mode
	"""
	while True:
		latitude, longitude = gps_module.read_GPS_position()
		writer.execute('''UPDATE gpslocation
			SET id = 0, latitude = ?, longitude = ?
			WHERE id=0''', [latitude, longitude])		
		#print('lat: {} - lng: {}'.format(latitude, longitude))

def reading_obd_data(obd_writer):
	"""Fuunction to manage OBD-II data in a multiprocesing thread
	
	First read the actual OBD-II data, then save this in TEMPORAL_OBD_DB

	Args:
		obd_writer (sqlite3.Connection): A sqlite3 connection in wal mode
	"""
	while True:
		# TODO: Uncomment code
		obd_data = None#obd_module.read_data()
		if obd_data == None:
			#print("OBD: No fue posible obtener los datos")
			continue
		else:
			speed, acc_pos = obd_data
			obd_writer.execute('''UPDATE obddata 
			SET id = 0, speed = ?, acc_pos=? 
			WHERE id=0''', [speed, acc_pos])

def saving_task (conn, cursor, reader, id_vehicle, t, trip_id, route):
	"""Save all captured data into sqlite database
	
	This function captured and save data from all modules
	(IMU, GPS, OBD-II), the data is saved into LOCAL_DB.
	
	Args:
		conn ([type]): [description]
		cursor ([type]): [description]
		reader ([type]): [description]
		id_vehicle ([type]): [description]
		t ([type]): [description]
		trip_id ([type]): [description]
		route ([type]): [description]
	"""
	# Load Kinematic data
	#kinematic_data = mpu6050.read_data()
	kinematic_data = mpu9250_module.read_data()
	accX, accY, accZ = kinematic_data[0]
	velAngX, velAngY, velAngZ = kinematic_data[1]
	magX, magY, magZ = kinematic_data[2]
	
	# Chek if near-crash button is pressed
	event_class = True if button.is_pressed else False
	
	# Load GPS data
	for row in reader.execute('SELECT * FROM gpslocation WHERE id=0 LIMIT 1'):
		latitude = row[1]
		longitude = row[2]
	
	# Load OBD data
	for row in obd_reader.execute('SELECT * FROM obddata WHERE id=0 LIMIT 1'):
		speed = row[1]
		acc_pos = row[2]
	
	# Insert data into database	
	data = [trip_id.value, "".join(id_vehicle.value), 
			"".join(route.value),
			int(time.time()*1000), speed,
			accX, accY, accZ, 
			velAngX, velAngY, velAngZ,
			magX, magY, magZ,
			latitude, longitude, 
			acc_pos, event_class, True
			]
	
	query = '''INSERT INTO vehicledata
			(
				idTrip, idVehicle, route, timestamp, speed,
				accX, accY,	accZ,
				velAngX, velAngY, velAngZ,
				magX, magY,	magZ,
				latitude, longitude, 
				accPosition, eventClass, active
			)
			VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'''
	
	cursor.execute(query, data)
	
	if ((time.time()-t.value) > 0.2 ):
		data_to_show["accX"]= accX
		data_to_show["accY"]= accY
		data_to_show["accZ"]= accZ
		data_to_show["velAngX"]= velAngX
		data_to_show["velAngY"]= velAngY
		data_to_show["velAngZ"]= velAngZ
		data_to_show["magX"]= magX
		data_to_show["magY"]= magY
		data_to_show["magZ"]= magZ
		data_to_show["lat"]= latitude
		data_to_show["lng"]= longitude
		data_to_show["speed"] = speed
		data_to_show["accPosition"] = acc_pos
		send_data(data_to_show)
		t.value = time.time()

def send_data(data_to_show):
	socketio.emit('vehicleData', json.dumps(data_to_show))

def get_last_trip ():
	cursor_db.execute("SELECT idTrip FROM vehicledata ORDER BY id DESC LIMIT 1")
	results = cursor_db.fetchall()
	last_trip = -1
	for row in results:
		last_trip = row[0]
	return last_trip


def modify_local_db_data(data):
	"""Calculate mean frequency and transform timestamp to string
	"""
	#transform_data = [dict(row) for row in data]
	for row in data:
		# Frequency data
		try:
			row['meanFrequency'] = round((row['capturedData'])*1000/(row['maxTime']-row['time']),2)
		except ZeroDivisionError as e:
			row['meanFrequency'] = 0
		# Time data
		row['time'] = datetime.datetime.fromtimestamp(row['time']/1000).strftime('%d-%b-%Y %H:%M')

	return data

def data_to_json(data):
	return dict(('row '+str(i), row) for i,row in enumerate(data,1))

def send_trip_data_firebase(data) -> bool:
	status = False
	try:
		trip_data = dict((k, data[k]) for k in list(data.keys())[0:] if k in data)
		trip_data["tripLocalId"] = trip_data["tripId"]
		del trip_data["tripId"]
		trip_data["device"] = "Raspberry"
		reference = ref.child('tripList').push(trip_data)
		query = f"""SELECT * FROM vehicledata WHERE idTrip = {data['tripId']}"""
		db_data = get_data(query)
		json_data = data_to_json(db_data)
		ref.child(f"tripData/raspberry/{reference.key}").set(json_data)
		status = True
	except:
		status = False
		print("ERROR FIREBASE: Upload data to firebase failed!")
	
	if status:
		hide_query = f"""UPDATE vehicledata SET active = 0 WHERE idTrip = {data['tripId']}"""
		execute_query(hide_query)
		return True;
	else:
		return False;

def delete_trip_data(data) -> bool:
	try: 
		delete_query = f"""DELETE FROM vehicledata WHERE idTrip = {data}"""
		execute_query(delete_query)
		return True
	except:
		return False

@app.route('/')
def index():
	current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
	templateData = {
		'title' : 'Vehicle data Recording'
	}
	return render_template('index.html', **templateData)

@app.route('/recordingTask', methods=['POST'])
def handleRecordingTask():
	global recording, connection_db, cursor_db, id_vehicle, route, period, time_elapsed
	request_data = request.get_json()
	recording = request_data['recording']
	id_vehicle.value = list(request_data['idVehicle'])
	route.value = list(request_data['route'])
	period.value = 1/int(request_data['freq'])

	response = 'Rpi is now {}'.format('recording' if (recording) else 'stopped')

	if(recording):
		global firstRecording, scheduler, reader, trip_id
		
		connection_db = create_connection()
		cursor_db = connection_db.cursor()
		trip_id.value = int(get_last_trip()) + 1
		
		time_elapsed.value = time.time()
		scheduler.add_job(saving_task, 
			args=[connection_db, cursor_db, reader, id_vehicle,
				time_elapsed, trip_id, route],
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


@app.route('/trips', methods=['GET', 'POST', 'DELETE'])
def trips():
	if request.method == 'POST':
		# If send button is presed
		request_data = request.get_json()
		response = send_trip_data_firebase(request_data)
		return {'result': response}
	
	elif request.method == 'DELETE':
		# If delete button is presed
		request_data = str(request.get_data(), 'utf-8')
		response = delete_trip_data(request_data)
		return {'result' : response}

	else:
		query = """SELECT 
					idTrip,
					MIN(timestamp) AS time,
					MAX(timestamp) AS maxTime,
					idVehicle,
					route,
					COUNT(accX) AS capturedData,
					SUM(eventClass) AS nearcrashesData,
					AVG(id) AS meanFrequency
				FROM vehicledata WHERE active = 1 GROUP BY idTrip
				"""
		db_data = get_data(query)
		data = modify_local_db_data(db_data)
		
		template_data = {
			'title': 'Trip History',
			'data' : data
		}
		return render_template('trips.html', **template_data)


@socketio.on('vehicleDataConnect')
def handle_connection(data):
	print('SOCKET: Incomming message: ' + data['data'])
	socketio.emit('vehicleDataConnect', json.dumps({"msg": "hola"}))


def main():
	try:
		create_databases()
		# Start 2 multiprocess
		location_p = Process(target=reading_gps_data, args=(writer,), daemon=True)
		obd_p = Process(target=reading_obd_data, args=(obd_writer,), daemon=True)
		location_p.start()
		obd_p.start()
		# Run principal thread app
		socketio.run(app, debug=True, port=8080, host='0.0.0.0', use_reloader=False)

	except KeyboardInterrupt:
		location_p.close()
		obd_p.close()

if __name__ == '__main__':
	main()
