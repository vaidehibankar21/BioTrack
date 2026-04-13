import os
import threading
from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from biotrack import predict_realtime
from database import save_reading, get_all_readings
from pdf_generator import generate_pdf_batch

import serial
import time
import re
from datetime import datetime

# ✅ Arduino connection
try:
    arduino = serial.Serial('COM3', 9600, timeout=1)
    time.sleep(2)
    print("✅ Arduino Connected on COM3")
except Exception as e:
    print(f"❌ Arduino Connection Error: {e}")
    arduino = None

app = Flask(__name__)
CORS(app)

# Global variables
readings_buffer = []
latest_vital = {
    "hr": 0,
    "spo2": 0,
    "status": "Initializing...",
    "patient": "Kritisha Oberoi"
}

# ---------------- SERIAL READ ---------------- #

def get_arduino_data():
    """
    Read HR & SpO2 from Arduino
    Time will be generated from Python (NOT Arduino)
    """
    if arduino and arduino.is_open:
        try:
            line = arduino.readline().decode(errors="ignore").strip()

            if line:
                print("RAW:", line)  # 🔥 Debug line

                # ✅ Only HR & SpO2 expected
                match = re.search(r"HR:\s*(\d+)\s*SpO2:\s*(\d+)", line)

                if match:
                    hr = int(match.group(1))
                    spo2 = int(match.group(2))

                    # ✅ TIME FROM PYTHON
                    current_time = datetime.now().strftime("%H:%M:%S")

                    return current_time, hr, spo2

        except Exception as e:
            print(f"⚠️ Serial Error: {e}")

    # fallback
    return datetime.now().strftime("%H:%M:%S"), 0, 0


# ---------------- API ROUTES ---------------- #

@app.route('/api/vitals', methods=['GET'])
def get_vitals():
    timestamp, hr, spo2 = get_arduino_data()

    data_to_send = {
        'time': timestamp,
        'hr': hr,
        'spo2': spo2,
        'status': predict_realtime(hr, spo2),
        'patient': 'Kritisha Oberoi'
    }

    print(f"Sending -> Time: {timestamp}, HR: {hr}, SpO2: {spo2}")
    return jsonify(data_to_send)


@app.route('/api/download-latest', methods=['GET'])
def download_latest():
    records_dir = os.path.join(os.getcwd(), 'records')

    if not os.path.exists(records_dir):
        return "Records folder not found.", 404

    files = [f for f in os.listdir(records_dir) if f.endswith('.pdf')]

    if not files:
        return "No reports found yet.", 404

    files.sort(reverse=True)
    return send_from_directory(records_dir, files[0])


@app.route("/readings", methods=["GET"])
def get_readings():
    return jsonify(get_all_readings())


@app.route('/api/list-reports', methods=['GET'])
def list_reports():
    records_dir = os.path.join(os.getcwd(), 'records')

    if not os.path.exists(records_dir):
        return jsonify([])

    files = [f for f in os.listdir(records_dir) if f.endswith('.pdf')]
    files.sort(reverse=True)

    return jsonify(files)


@app.route('/api/download-report/<filename>', methods=['GET'])
def download_specific_report(filename):
    records_dir = os.path.join(os.getcwd(), 'records')
    return send_from_directory(records_dir, filename)


# ---------------- SENSOR LOOP ---------------- #

def sensor_loop():
    global readings_buffer, latest_vital

    while True:
        timestamp, hr, spo2 = get_arduino_data()

        if hr > 0 or spo2 > 0:
            status = predict_realtime(hr, spo2)

            # Save to DB
            db_timestamp = save_reading(hr, spo2, status)

            latest_vital = {
                'hr': hr,
                'spo2': spo2,
                'status': status,
                'time': timestamp,
                'patient': "Kritisha Oberoi"
            }

            readings_buffer.append(latest_vital.copy())

            print(f"[LIVE] TIME={timestamp}, HR={hr}, SPO2={spo2}, STATUS={status}")

            # Generate PDF after 10 readings
            if len(readings_buffer) >= 10:
                print("[PDF] Generating report...")
                try:
                    pdf_file = generate_pdf_batch(readings_buffer)
                    print(f"[SUCCESS] PDF saved: {pdf_file}")
                except Exception as e:
                    print(f"[ERROR PDF] {e}")
                finally:
                    readings_buffer.clear()

        time.sleep(1)


# ---------------- MAIN ---------------- #

if __name__ == "__main__":
    if not os.path.exists('records'):
        os.makedirs('records')

    sensor_thread = threading.Thread(target=sensor_loop, daemon=True)
    sensor_thread.start()

    print("🚀 BioTrack Backend running at http://127.0.0.1:5000")

    app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)