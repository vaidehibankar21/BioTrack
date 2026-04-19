import os
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from biotrack import predict_realtime
from database import save_reading
from datetime import datetime

app = Flask(__name__)
CORS(app)

# --- DIRECTORY SETUP ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RECORDS_DIR = os.path.join(BASE_DIR, 'records')

if not os.path.exists(RECORDS_DIR):
    os.makedirs(RECORDS_DIR, exist_ok=True)

latest_vital = {
    "hr": 0, "spo2": 0, "status": "Waiting for data...",
    "patient": "Kritisha Oberoi", "time": "--:--:--"
}

@app.route('/')
def home():
    return "🚀 BioTrack Cloud Server is Live!"

@app.route('/api/update-vitals', methods=['POST'])
def update_vitals():
    global latest_vital
    try:
        data = request.json
        hr = int(data.get('hr', 0))
        spo2 = int(data.get('spo2', 0))
        
        status = predict_realtime(hr, spo2)
        save_reading(hr, spo2, status)
        
        latest_vital = {
            'hr': hr, 'spo2': spo2, 'status': status,
            'time': datetime.now().strftime("%H:%M:%S"),
            'patient': "Kritisha Oberoi"
        }
        return jsonify({"status": "success"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/vitals', methods=['GET'])
def get_vitals():
    return jsonify(latest_vital)

# This part only runs if you start the script manually
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
