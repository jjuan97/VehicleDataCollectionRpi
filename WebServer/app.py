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

scheduler = BackgroundScheduler(timezone="America/Bogota", job_defaults={'max_instances': 2})
recording = False
firstRecording = True
tempState = [0, 0, True]
data = {"accX": 12.34, "accY": 12.12, "lat": 0, "lng": 0}


def modifyData (tempState):
    while tempState[2]:
        i = random.randrange(10)
        print('Recording: {}, i={}'.format(tempState[2], i))
        if (i%2 == 0):
            tempState[0] = i
            tempState[1] = i
        time.sleep(0.1)

def sendingData (data, tempState):
    print(tempState)
    data['lat'] = tempState[0]
    data["lng"] = tempState[1]
    socketio.emit('vehicleData', json.dumps(data))

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
    global recording
    # TODO: start savingTask
    request_data = request.get_json()
    recording = request_data['recording']
    tempState[2] = recording
    idVehicle = request_data['idVehicle']
    freq = request_data['freq']

    response = 'Rpi is now {}'.format('recording' if (recording) else 'stopped')

    if(recording):
        global firstRecording, scheduler

        scheduler.add_job(sendingData, args=[data, tempState], trigger='interval', seconds=1, id="send_data")
        scheduler.add_job(modifyData, args=[tempState], trigger='date', id="modify_data")
        if (firstRecording):
            scheduler.start()
            firstRecording = False;
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
    socketio.run(app, debug=True, port=80, host='0.0.0.0')
    # app.run(debug=True, port=80, host='0.0.0.0')
