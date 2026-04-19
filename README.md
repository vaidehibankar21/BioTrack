# ❤️ BioTrack: Smart Healthcare Monitoring System

BioTrack is a real-time health monitoring solution that tracks **Heart Rate (BPM)** and **Oxygen Saturation (SpO₂)** using IoT sensors and Machine Learning. It classifies health conditions as **Normal** or **Abnormal** using a hybrid approach of Random Forest classification and clinical rule-based logic.

### 🚀 [Live Dashboard (Frontend)](https://biotrack-eight.vercel.app/) | 🔗 [Cloud Server (Backend)](https://biotrack-zrpl.onrender.com)

---

## ✨ Features
* **Real-time Monitoring:** Streams live vitals from hardware sensors to a web dashboard via a Flask cloud server.
* **Hybrid Intelligence:** Combines a **Random Forest Classifier** with **Clinical Safety Rules** for high-accuracy health labeling.
* **Automated PDF Reports:** Generates a detailed health report with data tables and trend graphs every 10 readings.
* **Visual Analytics:** Responsive React dashboard with live status updates and historical report downloads.
* **Smart Alerts:** Detects Bradycardia (Low HR), Tachycardia (High HR), and Hypoxia (Low SpO₂).

---

## 🛠️ Tech Stack

### **Frontend**
* **React.js** (Hosted on Vercel)

### **Backend**
* **Python / Flask** (Hosted on Render)
* **Scikit-Learn** (Machine Learning)
* **Matplotlib** (PDF Generation)
* **Gunicorn** (Production Server)

### **Hardware/IoT**
* **MAX30102** Pulse Oximeter Sensor
* **Arduino** (for data acquisition)
* **Python Serial Bridge** (to push local data to the cloud)

---

## 📊 Health Classification Logic
BioTrack uses a strict medical safety layer to ensure data reliability:

| Vital | Normal Range | Abnormal Trigger |
| :--- | :--- | :--- |
| **Heart Rate** | 60 - 100 BPM | < 50 BPM (Low) or > 100 BPM (High) |
| **SpO₂** | 95 - 100% | < 95% (Low) |
| **Sensor Status** | - | SpO₂ = 0% (No Finger Detected) |
