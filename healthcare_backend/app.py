import os
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from biotrack import predict_realtime
from database import save_reading, get_all_readings
from pdf_generator import generate_pdf_batch
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
        
        # Calling the improved logic
        status = predict_realtime(hr, spo2)
        
        save_reading(hr, spo2, status)
        
        timestamp = datetime.now().strftime("%H:%M:%S")
        latest_vital = {
            'hr': hr, 'spo2': spo2, 'status': status,
            'time': timestamp,
            'patient': "Kritisha Oberoi"
        }

        # PDF Trigger Logic
        all_data = get_all_readings()
        if len(all_data) > 0 and len(all_data) % 10 == 0:
            batch = all_data[-10:]
            formatted_batch = [{
                'hr': d['heart_rate'], 
                'spo2': d['spo2'], 
                'status': d['status'], 
                'time': d['time']
            } for d in batch]
            generate_pdf_batch(formatted_batch)

        return jsonify({"status": "success"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/vitals', methods=['GET'])
def get_vitals():
    return jsonify(latest_vital)

@app.route('/api/list-reports', methods=['GET'])
def list_reports():
    try:
        files = [f for f in os.listdir(RECORDS_DIR) if f.endswith('.pdf')]
        return jsonify(sorted(files, reverse=True))
    except Exception:
        return jsonify([])

@app.route('/api/download-report/<filename>', methods=['GET'])
def download_report(filename):
    try:
        return send_from_directory(RECORDS_DIR, filename)
    except Exception as e:
        return str(e), 404

@app.route('/api/download-latest', methods=['GET'])
def download_latest():
    try:
        files = [f for f in os.listdir(RECORDS_DIR) if f.endswith('.pdf')]
        if not files:
            return "No reports generated yet.", 404
        latest_file = max([os.path.join(RECORDS_DIR, f) for f in files], key=os.path.getctime)
        return send_from_directory(RECORDS_DIR, os.path.basename(latest_file))
    except Exception as e:
        return str(e), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
