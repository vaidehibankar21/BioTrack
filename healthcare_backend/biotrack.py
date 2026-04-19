# -*- coding: utf-8 -*-

# BioTrack: Smart Healthcare Monitoring System using HR & SpO₂
"""
This project focuses on building a smart healthcare monitoring system that classifies a person's health condition as **Normal** or **Abnormal** using:

- ❤️ Heart Rate (HR)
- 🫁 Oxygen Saturation (SpO₂)


- Machine Learning model trained on HR and SpO₂
- Real-time prediction compatible with sensor data
- Hybrid system using **Machine Learning + Rule-based safety**

---
"""
# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import re
import os
from sklearn.ensemble import RandomForestClassifier

# --- PATH FIX ---
# This finds the 'data' folder regardless of where Render runs the script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

files = [
    ("s10_sit","Sit","S10"), ("s10_walk","Walk","S10"), ("s10_run","Run","S10"),
    ("s11_sit","Sit","S11"), ("s11_walk","Walk","S11"), ("s11_run","Run","S11"),
    ("s12_sit","Sit","S12"), ("s12_walk","Walk","S12"), ("s12_run","Run","S12"),
]

model = None

def extract_meta(file):
    file_path = os.path.join(BASE_DIR, "data", f"{file}.hea")
    
    # If files are missing on the server, use these defaults so it doesn't crash
    if not os.path.exists(file_path):
        defaults = {"sit": (72, 98), "walk": (95, 97), "run": (145, 95)}
        activity_type = file.split("_")[1] if "_" in file else "sit"
        return defaults.get(activity_type, (75, 98))
    try:
        with open(file_path, "r") as f:
            text = f.read()
        hr = int(re.search(r'hr_1_start>: (\d+)', text).group(1))
        spo2 = int(re.search(r'spo2_start>: (\d+)', text).group(1))
        return hr, spo2
    except Exception:
        return 75, 98

def train_model():
    """Lazy Loader: Trains the model only when the first data arrives"""
    global model
    print("🔄 Training BioTrack Model...")
    data = []
    for file, activity, subject in files:
        hr, spo2 = extract_meta(file)
        data.append([subject, activity, hr, spo2])

    df = pd.DataFrame(data, columns=["Subject","Activity","HR","SpO2"])
    df_expanded = pd.concat([df]*50, ignore_index=True)
    df_expanded['HR'] += np.random.normal(0, 5, len(df_expanded))
    df_expanded['SpO2'] += np.random.normal(0, 1, len(df_expanded))
    
    X = df_expanded[['HR','SpO2']]
    y = df_expanded.apply(lambda r: "Abnormal" if r['SpO2'] < 95 or r['HR'] > 100 or r['HR'] < 60 else "Normal", axis=1)
    
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X, y)
    print("✅ Training Complete.")

def predict_realtime(hr, spo2):
    global model
    if model is None:
        train_model()
    
    # Safety rules (Run instantly)
    if spo2 < 95: return "Abnormal (Low SpO2)"
    if hr > 100: return "Abnormal (High HR)"
    if hr < 60: return "Abnormal (Low HR)"

    input_df = pd.DataFrame([[hr, spo2]], columns=['HR','SpO2'])
    return model.predict(input_df)[0]
