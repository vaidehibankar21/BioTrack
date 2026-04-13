# serial_reader.py
import time
import random
from config import SERIAL_PORT, BAUD_RATE, USE_ARDUINO

if USE_ARDUINO:
    import serial

def read_sensor_data():
    if USE_ARDUINO:
        try:
            print(f"Connecting to {SERIAL_PORT}...")
            ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
            time.sleep(2)
            print("Connected to Arduino...")

            while True:
                line = ser.readline().decode(errors="ignore").strip()
                if line:
                    try:
                        parts = line.split(",")
                        hr = int(parts[0].split(":")[1])
                        spo2 = int(parts[1].split(":")[1])
                        yield hr, spo2
                    except Exception as e:
                        print("Parse Error:", e)
                        continue
        except Exception as e:
            print("Serial Error:", e)
    else:
        # Simulation mode
        print("Simulation Mode ON")
        while True:
            hr = random.randint(70, 120)
            spo2 = random.randint(90, 100)
            print(f"[SIMULATED DATA] HR={hr}, SPO2={spo2}")
            time.sleep(2)
            yield hr, spo2