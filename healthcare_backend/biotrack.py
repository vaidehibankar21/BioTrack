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

# BioTrack: Smart Healthcare Monitoring System using HR & SpO₂
"""
Machine Learning + Rule-based safety logic for health classification.
Fixed for Cloud Deployment (Render) with Lazy Loading.
"""

import pandas as pd
import numpy as np
import re
import os
import joblib
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

# Dataset files configuration
files = [
    ("s10_sit","Sit","S10"), ("s10_walk","Walk","S10"), ("s10_run","Run","S10"),
    ("s11_sit","Sit","S11"), ("s11_walk","Walk","S11"), ("s11_run","Run","S11"),
    ("s12_sit","Sit","S12"), ("s12_walk","Walk","S12"), ("s12_run","Run","S12"),
]

# Global model variable to allow lazy loading
model = None

def extract_meta(file):
    file_path = os.path.join("data", f"{file}.hea")
    if not os.path.exists(file_path):
        defaults = {"sit": (72, 98), "walk": (95, 97), "run": (145, 95)}
        activity_type = file.split("_")[1]
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
    """Trains the model only when first called to prevent startup timeout"""
    global model
    print("🔄 Starting BioTrack Model Training...")
    data = []
    for file, activity, subject in files:
        hr, spo2 = extract_meta(file)
        data.append([subject, activity, hr, spo2])

    df = pd.DataFrame(data, columns=["Subject","Activity","HR","SpO2"])
    df = df.drop_duplicates().reset_index(drop=True)

    df_expanded = pd.concat([df]*50, ignore_index=True)
    df_expanded['HR'] += np.random.normal(0, 5, len(df_expanded))
    df_expanded['SpO2'] += np.random.normal(0, 1, len(df_expanded))
    df_expanded['HR'] = df_expanded['HR'].clip(40, 180)
    df_expanded['SpO2'] = df_expanded['SpO2'].clip(80, 100)

    def label(row):
        if row['SpO2'] < 95 or row['HR'] > 100 or row['HR'] < 60:
            return "Abnormal"
        return "Normal"

    df_expanded['Label'] = df_expanded.apply(label, axis=1)
    
    # Borderline & Synthetic Data
    borderline = []
    for _ in range(100):
        borderline.append(["Border","Mixed", np.random.randint(95, 105), np.random.randint(94, 96), np.random.choice(["Normal","Abnormal"])])
    df_border = pd.DataFrame(borderline, columns=["Subject","Activity","HR","SpO2","Label"])

    abnormal_data = []
    for _ in range(150):
        abnormal_data.append(["Synthetic","Critical", np.random.randint(110, 160), np.random.randint(85, 93), "Abnormal"])
    df_abnormal = pd.DataFrame(abnormal_data, columns=["Subject","Activity","HR","SpO2","Label"])

    final_df = pd.concat([df_expanded, df_border, df_abnormal], ignore_index=True)
    
    X = final_df[['HR','SpO2']]
    y = final_df['Label']
    
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X, y)
    print("✅ BioTrack Model Training Complete!")

def predict_realtime(hr, spo2):
    global model
    if model is None:
        train_model()

    hr = max(0, min(hr, 220))
    spo2 = max(0, min(spo2, 100))

    if spo2 < 95: return "Abnormal (Low SpO2)"
    if hr > 100: return "Abnormal (High HR)"
    if hr < 60: return "Abnormal (Low HR)"

    input_df = pd.DataFrame([[hr, spo2]], columns=['HR','SpO2'])
    return model.predict(input_df)[0]
