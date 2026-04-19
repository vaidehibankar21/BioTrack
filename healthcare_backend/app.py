import os
from flask import Flask, jsonify, send_from_directory, request
from flask_cors import CORS
from biotrack import predict_realtime
from database import save_reading, get_all_readings
from pdf_generator import generate_pdf_batch
from datetime import datetime

# NOTE: No 'import serial' here. Serial is handled by bridge.py on your laptop.

app = Flask(__name__)
CORS(app)

# --- CRITICAL FIX FOR RENDER ---
# Move folder creation OUTSIDE of __main__ so Gunicorn creates it on startup
RECORDS_DIR = os.path.join(os.getcwd(), 'records')
if not os.path.exists(RECORDS_DIR):
    os.makedirs(RECORDS_DIR)
# -------------------------------

# Global variables to store data coming from your hardware via bridge.py
readings_buffer = []
latest_vital = {
    "hr": 0,
    "spo2": 0,
    "status": "Waiting for Arduino...",
    "patient": "Kritisha Oberoi",
    "time": "--:--:--"
}

# ---------------- API ROUTES ---------------- #

# ✅ HOME ROUTE: Prevents the "Not Found" error on the main URL
@app.route('/')
def home():
    return "🚀 BioTrack Cloud Server is Live! Please run bridge.py on your laptop."

# ✅ HARDWARE RECEIVER: This is where bridge.py sends Arduino data
@app.route('/api/update-vitals', methods=['POST'])
def update_vitals():
    global readings_buffer, latest_vital
    try:
        data = request.json
        hr = int(data.get('hr', 0))
        spo2 = int(data.get('spo2', 0))
        timestamp = datetime.now().strftime("%H:%M:%S")

        if hr > 0 or spo2 > 0:
            # 1. Run Machine Learning Model
            status = predict_realtime(hr, spo2)

            # 2. Save to Database
            save_reading(hr, spo2, status)

            # 3. Update the global "Latest" state for the Dashboard
            latest_vital = {
                'hr': hr,
                'spo2': spo2,
                'status': status,
                'time': timestamp,
                'patient': "Kritisha Oberoi"
            }

            # 4. Add to buffer for PDF generation
            readings_buffer.append(latest_vital.copy())

            print(f"[DATA RECEIVED] HR: {hr}, SpO2: {spo2}, Status: {status}")

            # 5. Generate PDF after every 10 readings
            if len(readings_buffer) >= 10:
                print("[PDF] Generating automated report...")
                try:
                    pdf_file = generate_pdf_batch(readings_buffer)
                    print(f"[SUCCESS] PDF Generated: {pdf_file}")
                except Exception as e:
                    print(f"[ERROR PDF] {e}")
                finally:
                    readings_buffer.clear()

        return jsonify({"status": "success"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# ✅ DASHBOARD FEED: React calls this to show data on the screen
@app.route('/api/vitals', methods=['GET'])
def get_vitals():
    return jsonify(latest_vital)

@app.route('/api/download-latest', methods=['GET'])
def download_latest():
    if not os.path.exists(RECORDS_DIR):
        return "Records folder not found.", 404
    files = [f for f in os.listdir(RECORDS_DIR) if f.endswith('.pdf')]
    if not files:
        return "No reports found yet.", 404
    files.sort(reverse=True)
    return send_from_directory(RECORDS_DIR, files[0])

@app.route("/readings", methods=["GET"])
def get_readings():
    return jsonify(get_all_readings())

@app.route('/api/list-reports', methods=['GET'])
def list_reports():
    if not os.path.exists(RECORDS_DIR):
        return jsonify([])
    files = [f for f in os.listdir(RECORDS_DIR) if f.endswith('.pdf')]
    files.sort(reverse=True)
    return jsonify(files)

@app.route('/api/download-report/<filename>', methods=['GET'])
def download_specific_report(filename):
    return send_from_directory(RECORDS_DIR, filename)

# ---------------- MAIN ---------------- #

if __name__ == "__main__":
    # Render uses an environment variable for PORT
    port = int(os.environ.get("PORT", 5000))
    print(f"🚀 BioTrack Backend starting on port {port}")
    app.run(host="0.0.0.0", port=port, debug=False)
