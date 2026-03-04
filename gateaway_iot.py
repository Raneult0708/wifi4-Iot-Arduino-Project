import serial, json, threading, time
from flask import Flask, jsonify, render_template
from collections import deque

PORT_SERIE = '/dev/ttyACM0'
BAUDRATE   = 9600
app        = Flask(__name__)
historique = deque(maxlen=50)
derniere   = {}

def lire_arduino():
    try:
        ser = serial.Serial(PORT_SERIE, BAUDRATE, timeout=2)
        print(f"[OK] Port série ouvert : {PORT_SERIE}")
        while True:
            try:
                ligne = ser.readline().decode('utf-8').strip()
                data  = json.loads(ligne)
                data['ts'] = time.strftime('%H:%M:%S')
                historique.append(data)
                global derniere
                derniere = data
                print(f"[DATA] {data}")
            except Exception:
                pass
    except Exception as e:
        print(f"[ERREUR Serial] {e}")

@app.route('/data')
def get_data():
    return jsonify({'actuel': derniere, 'historique': list(historique)})

@app.route('/')
def dashboard():
    return render_template('dashboard.html')  # cherche dans templates/

if __name__ == '__main__':
    t = threading.Thread(target=lire_arduino, daemon=True)
    t.start()
    app.run(host='0.0.0.0', port=5000, debug=False)