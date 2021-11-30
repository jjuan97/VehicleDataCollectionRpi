from flask import Flask, render_template
import datetime

app = Flask(__name__)

@app.route('/')
def index():
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

    templateData = {
        'title' : 'Hello Bulma',
        'time' : current_time,
        'latitude' : 0.80,
        'longitude' : -77.3,
        'accX' : 0.00009,
        'accY' : 0.29,
        'accZ' : 9.87,
    }

    return render_template('index.html', **templateData)
if __name__ == '__main__':
    app.run(debug=True, port=80, host='0.0.0.0')
