from os import truncate
from flask import Flask, render_template, request
from flask_socketio import SocketIO
from flask import g
from apscheduler.schedulers.background import BackgroundScheduler

import eventlet
import datetime
import json
import random
import time
import sqlite3
import firebase_admin

from firebase_admin import credentials
from firebase_admin import db

# Firebase configuration
cred = credentials.Certificate("./vehicledatacollected-firebase-adminsdk-dfzqq-f41fc7bb31.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://vehicledatacollected-default-rtdb.firebaseio.com'
})
ref = db.reference('/')

# Scheduler and web socket configuration
eventlet.monkey_patch(thread=True, time=True)
app = Flask(__name__)
socketio = SocketIO(app)

scheduler = BackgroundScheduler(
    timezone="America/Bogota", job_defaults={'max_instances': 2})
recording = False
first_recording = True
temp_state = [0, 0, True]
data = {"accX": 12.34, "accY": 12.12, "lat": 0, "lng": 0}

# DATABASE functions (connect, close, and get_data)
DATABASE = './database/vehicledatabase.db'

def sqlite_dict(cursor, row):
    return dict((cursor.description[idx][0], value)
                for idx, value in enumerate(row))

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    db.row_factory = sqlite_dict
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def get_data(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

def delete_data(query):
    conn = get_db()
    cur = conn.cursor()
    cur.execute(query)
    cur.close()
    conn.commit()

def modify_local_db_data(data):
    """Calculate mean frequency and transform timestamp to string
    """
    #transform_data = [dict(row) for row in data]
    for row in data:
        # Frequency data
        try:
            row['meanFrequency'] = round((row['capturedData']*1000)/(row['maxTime']-row['time']),2)
        except ZeroDivisionError as e:
            row['meanFrequency'] = 0
        # Time data
        row['time'] = datetime.datetime.fromtimestamp(row['time']).strftime('%Y-%m-%d %H:%M')

    return data

def modify_data(temp_state):
    while temp_state[2]:
        i = random.randrange(10)
        print('Recording: {}, i={}'.format(temp_state[2], i))
        if (i % 2 == 0):
            temp_state[0] = i
            temp_state[1] = i
        time.sleep(0.1)

def data_to_json(data):
    return dict(('row '+str(i), row) for i,row in enumerate(data,1))

def sending_data(data, temp_state):
    print(temp_state)
    data['lat'] = temp_state[0]
    data["lng"] = temp_state[1]
    socketio.emit('vehicleData', json.dumps(data))

def send_trip_data_firebase(data) -> bool:
    status = False
    try:
        trip_data = dict((k, data[k]) for k in list(data.keys())[1:] if k in data)
        reference = ref.child('tripList').push(trip_data)
        query = f"""SELECT * FROM vehicledata WHERE idTrip = {data['tripId']}"""
        db_data = get_data(query)
        json_data = data_to_json(db_data)
        ref.child(f"tripData/raspberry/{reference.key}").set(json_data)
        status = True
    except:
        status = False
        print("Upload data to firebase failed!")
    
    if status:
        delete_query = f"""DELETE FROM vehicledata WHERE idTrip = {data['tripId']}"""
        delete_data(delete_query)
        return True;
    else:
        return False;

def delete_trip_data(data) -> bool:
    try: 
        delete_query = f"""DELETE FROM vehicledata WHERE idTrip = {data}"""
        delete_data(delete_query)
        return True
    except:
        return False

@app.route('/')
def index():
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

    template_data = {
        'title': 'Vehicle data Recording',
        'time': current_time,
        'latitude': 0.80,
        'longitude': -77.3,
        'accX': 0.00009,
        'accY': 0.29,
        'accZ': 9.87,
    }
    return render_template('index.html', **template_data)


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
                    COUNT(accX) AS capturedData,
                    SUM(eventClass) AS nearcrashesData,
                    AVG(id) AS meanFrequency
                FROM vehicledata GROUP BY idTrip
                """
        db_data = get_data(query)
        data = modify_local_db_data(db_data)
        
        template_data = {
            'title': 'Trip History',
            'data' : data
        }
        return render_template('trips.html', **template_data)

@app.route('/recordingTask', methods=['POST'])
def handle_recording_task():
    global recording
    # TODO: start savingTask
    request_data = request.get_json()
    recording = request_data['recording']
    temp_state[2] = recording
    idVehicle = request_data['idVehicle']
    freq = request_data['freq']

    response = 'Rpi is now {}'.format(
        'recording' if (recording) else 'stopped')

    if(recording):
        global first_recording, scheduler

        scheduler.add_job(sending_data, args=[
                          data, temp_state], trigger='interval', seconds=1, id="send_data")
        scheduler.add_job(modify_data, args=[
                          temp_state], trigger='date', id="modify_data")
        if (first_recording):
            scheduler.start()
            first_recording = False
        else:
            scheduler.resume()
    else:
        scheduler.pause()
        scheduler.remove_all_jobs()

    socketio.emit('vehicleData', json.dumps({"response": response}))
    return {"response": response}


@socketio.on('vehicleData')
def handle_connection(data):
    print('Incomming message: ' + data['data'])
    socketio.emit('vehicleData', json.dumps({"msg": "hola"}))


if __name__ == '__main__':
    socketio.run(app, debug=True, port=8080, host='0.0.0.0')
    # app.run(debug=True, port=80, host='0.0.0.0')
