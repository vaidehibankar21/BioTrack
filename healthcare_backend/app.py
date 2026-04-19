import os
from flask import Flask, jsonify, send_from_directory, request
from flask_cors import CORS
from biotrack import predict_realtime
from database import save_reading, get_all_readings
from pdf_generator import generate_pdf_batch
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Ensure folders exist globally for Gunicorn
RECORDS_DIR = os.path.join(os.getcwd(), 'records')
if not os.path.exists(RECORDS_DIR):
    os.makedirs(RECORDS_DIR)

readings_buffer = []
latest_vital = {
    "hr": 0, "spo2": 0, "status": "Waiting for Arduino...",
    "patient": "Kritisha Oberoi", "time": "--:--:--"
}

@app.route('/')
def home():
    return "🚀 BioTrack Cloud Server is Live! Please run bridge.py on your laptop."

@app.route('/api/update-vitals', methods=['POST'])
def update_vitals():
    global readings_buffer, latest_vital
    try:
        data = request.json
        hr = int(data.get('hr', 0))
        spo2 = int(data.get('spo2', 0))
        timestamp = datetime.now().strftime("%H:%M:%S")

        if hr > 0 or spo2 > 0:
            status = predict_realtime(hr, spo2)
            save_reading(hr, spo2, status)
            latest_vital = {
                'hr': hr, 'spo2': spo2, 'status': status,
                'time': timestamp, 'patient': "Kritisha Oberoi"
            }
            readings_buffer.append(latest_vital.copy())

            if len(readings_buffer) >= 10:
                generate_pdf_batch(readings_buffer)
                readings_buffer.clear()

        return jsonify({"status": "success"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/vitals', methods=['GET'])
def get_vitals():
    return jsonify(latest_vital)

@app.route('/api/download-latest', methods=['GET'])
def download_latest():
    files = [f for f in os.listdir(RECORDS_DIR) if f.endswith('.pdf')]
    if not files: return "No reports found yet.", 404
    files.sort(reverse=True)
    return send_from_directory(RECORDS_DIR, files[0])

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
