# -*- coding: utf-8 -*-

# BioTrack: Smart Healthcare Monitoring System using HR & SpO₂
"""
This project focuses on building a smart healthcare monitoring system that classifies a person's health condition as **Normal** or **Abnormal** using:

- ❤️ Heart Rate (HR)
- 🫁 Oxygen Saturation (SpO₂)



- Data extracted from PhysioNet dataset (.hea files)
- Machine Learning model trained on HR and SpO₂
- Real-time prediction compatible with sensor data
- Hybrid system using **Machine Learning + Rule-based safety**

---
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import re
import os
import joblib

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

# Dataset files configuration
files = [
    ("s10_sit","Sit","S10"),
    ("s10_walk","Walk","S10"),
    ("s10_run","Run","S10"),
    ("s11_sit","Sit","S11"),
    ("s11_walk","Walk","S11"),
    ("s11_run","Run","S11"),
    ("s12_sit","Sit","S12"),
    ("s12_walk","Walk","S12"),
    ("s12_run","Run","S12"),
]

data = []

def extract_meta(file):
    """Extract HR and SpO2 from .hea files"""
    # Added error handling for file reading
    file_path = os.path.join("data", f"{file}.hea")
    try:
        with open(file_path, "r") as f:
            text = f.read()
        hr = int(re.search(r'hr_1_start>: (\d+)', text).group(1))
        spo2 = int(re.search(r'spo2_start>: (\d+)', text).group(1))
        return hr, spo2
    except Exception as e:
        print(f"Error reading {file}: {e}")
        return 75, 98  # Fallback defaults

# 1. Create Base Dataset
for file, activity, subject in files:
    hr, spo2 = extract_meta(file)
    data.append([subject, activity, hr, spo2])

df = pd.DataFrame(data, columns=["Subject","Activity","HR","SpO2"])
df = df.drop_duplicates().reset_index(drop=True)

# 2. Data Expansion & Realistic Noise
df_expanded = pd.concat([df]*50, ignore_index=True)
df_expanded['HR'] += np.random.normal(0, 5, len(df_expanded))
df_expanded['SpO2'] += np.random.normal(0, 1, len(df_expanded))

# Clip values to realistic human range
df_expanded['HR'] = df_expanded['HR'].clip(40, 180)
df_expanded['SpO2'] = df_expanded['SpO2'].clip(80, 100)

# 3. FIXED LABELING LOGIC
def label(row):
    """
    Classifies data for training. 
    Matches the medical standards used in the PDF report.
    """
    # Rule 1: SpO2 below 95% is Abnormal
    if row['SpO2'] < 95:
        return "Abnormal"
    # Rule 2: HR outside 60-100 range is Abnormal (FIXED: Use 'or', not 'and')
    elif row['HR'] > 100 or row['HR'] < 60:
        return "Abnormal"
    else:
        return "Normal"

df_expanded['Label'] = df_expanded.apply(label, axis=1)

# 4. Adding Borderline & Synthetic Abnormal Data
borderline = []
for _ in range(100):
    hr = np.random.randint(95, 105) # Near the 100 threshold
    spo2 = np.random.randint(94, 96) # Near the 95 threshold
    # Randomly label borderline to help ML handle uncertainty
    lbl = np.random.choice(["Normal","Abnormal"])
    borderline.append(["Border","Mixed", hr, spo2, lbl])

df_border = pd.DataFrame(borderline, columns=["Subject","Activity","HR","SpO2","Label"])

abnormal_data = []
for _ in range(150):
    hr = np.random.randint(110, 160)
    spo2 = np.random.randint(85, 93)
    abnormal_data.append(["Synthetic","Critical", hr, spo2, "Abnormal"])

df_abnormal = pd.DataFrame(abnormal_data, columns=["Subject","Activity","HR","SpO2","Label"])

# 5. Final Dataset Preparation
final_df = pd.concat([df_expanded, df_border, df_abnormal], ignore_index=True)

# 6. Model Training
X = final_df[['HR','SpO2']]
y = final_df['Label']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

print(f"Model Trained. Accuracy: {accuracy_score(y_test, model.predict(X_test)):.2f}")

#7. REAL-TIME PREDICTION
def predict_realtime(hr, spo2):
    """
    Hybrid logic: Rule-based safety first, then ML check.
    """
    # Clean input data
    hr = max(0, min(hr, 220))
    spo2 = max(0, min(spo2, 100))

    # Rule-based safety: Instant Abnormal triggers (Synced with PDF)
    if spo2 < 95:
        return "Abnormal (Low SpO2)"

    if hr > 100:
        return "Abnormal (High HR)"

    if hr < 60:
        return "Abnormal (Low HR)"

    # Use ML for stable/borderline readings
    input_df = pd.DataFrame([[hr, spo2]], columns=['HR','SpO2'])
    return model.predict(input_df)[0]

# Sample Tests
if __name__ == "__main__":
    print(f"Testing 85 BPM, 98% SpO2: {predict_realtime(85, 98)}") # Normal
    print(f"Testing 120 BPM, 96% SpO2: {predict_realtime(120, 96)}") # Abnormal (High HR)
    print(f"Testing 75 BPM, 92% SpO2: {predict_realtime(75, 92)}") # Abnormal (Low SpO2)
    print(predict_realtime(202,45))
