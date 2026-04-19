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
import pandas as pd
import numpy as np
import re
import os
from sklearn.ensemble import RandomForestClassifier

# Path fix for data folder
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

files = [
    ("s10_sit","Sit","S10"), ("s10_walk","Walk","S10"), ("s10_run","Run","S10"),
    ("s11_sit","Sit","S11"), ("s11_walk","Walk","S11"), ("s11_run","Run","S11"),
    ("s12_sit","Sit","S12"), ("s12_walk","Walk","S12"), ("s12_run","Run","S12"),
]

model = None

def extract_meta(file):
    file_path = os.path.join(BASE_DIR, "data", f"{file}.hea")
    if not os.path.exists(file_path):
        return 75, 98 # Fallback
    try:
        with open(file_path, "r") as f:
            text = f.read()
        hr = int(re.search(r'hr_1_start>: (\d+)', text).group(1))
        spo2 = int(re.search(r'spo2_start>: (\d+)', text).group(1))
        return hr, spo2
    except:
        return 75, 98

def train_model():
    global model
    data = []
    for file, activity, subject in files:
        hr, spo2 = extract_meta(file)
        data.append([hr, spo2])
    
    df = pd.DataFrame(data, columns=['HR','SpO2'])
    y = df.apply(lambda r: "Abnormal" if r['SpO2'] < 95 or r['HR'] > 100 else "Normal", axis=1)
    
    model = RandomForestClassifier(n_estimators=50)
    model.fit(df, y)

def predict_realtime(hr, spo2):
    global model
    if model is None:
        train_model()
    
    # Safety hard-rules
    if spo2 < 95: return "Abnormal (Low SpO2)"
    if hr > 100: return "Abnormal (High HR)"
    
    input_df = pd.DataFrame([[hr, spo2]], columns=['HR','SpO2'])
    return model.predict(input_df)[0]
