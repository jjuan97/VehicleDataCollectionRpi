from flask import Flask, render_template, request
from flask_socketio import SocketIO
from apscheduler.schedulers.background import BackgroundScheduler

import eventlet
import datetime
import json
import random
import time

eventlet.monkey_patch(thread=True, time=True)
app = Flask(__name__)
socketio = SocketIO(app)
recording = False
scheduler = BackgroundScheduler(timezone="America/Bogota", job_defaults={'max_instances': 2})
firstRecording = True

gpsData = [0, 0]
data = {"accX": 12.34, "accY": 12.12, "lat": 0, "lng": 0}


def modifyData (gpsData):
    while True:
        i = random.randrange(10)
        #print(i)
        gpsData[0] = i
        gpsData[1] = i
        time.sleep(0.2)
    

def sendingData (data, gpsData):
    #print(gpsData)
    data['lat'] = gpsData[0]
    data["lng"] = gpsData[1]
    socketio.emit('vehicleData', json.dumps(data))

#scheduler.add_job(sendingData, args=[data, gpsData], trigger='interval', seconds=1, id="send_data")
#scheduler.add_job(modifyData, args=[gpsData], trigger='date', id="modify_data")

@app.route('/')
def index():
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

    templateData = {
        'title' : 'Vehicle data Recording',
        'time' : current_time,
        'latitude' : 0.80,
        'longitude' : -77.3,
        'accX' : 0.00009,
        'accY' : 0.29,
        'accZ' : 9.87,
    }
    return render_template('index.html', **templateData)


@app.route('/recordingTask', methods=['POST'])
def handleRecordingTask():  

    # TODO: start savingTask
    request_data = request.get_json()
    recording = request_data['recording']
    idVehicle = request_data['idVehicle']
    freq = request_data['freq']

    response = 'Rpi is now {}'.format('recording' if (recording) else 'stopped')

    if(recording):
        #scheduler.add_job(sendingData, 'interval', seconds=1, id="send_data")
        global firstRecording, scheduler
        scheduler.add_job(sendingData, args=[data, gpsData], trigger='interval', seconds=1)
        scheduler.add_job(modifyData, args=[gpsData], trigger='date', id='2')
        if (firstRecording):
            scheduler.start()
            firstRecording = False;
        else:
            scheduler.resume()
    else:
        scheduler.pause()
        scheduler.pause_job('2')
        scheduler.remove_all_jobs()
        #scheduler.reschedule_job('send_data', trigger='interval', seconds=1)

    socketio.emit('vehicleData', json.dumps({"response": response}))
    return {"response": response}


@socketio.on('vehicleData')
def handle_connection(data):
    print('Incomming message: ' + data['data'])
    socketio.emit('vehicleData', json.dumps({"msg": "hola"}))

if __name__ == '__main__':
    socketio.run(app, debug=True, port=80, host='0.0.0.0')
    # app.run(debug=True, port=80, host='0.0.0.0')
