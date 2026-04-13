# database.py
from datetime import datetime

# In-memory storage for readings
data_store = []

MAX_SIZE = 1000  # Prevent memory overflow

def save_reading(hr, spo2, status):
    """
    Save a sensor reading to memory and return timestamp
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = {
        "time": timestamp,
        "heart_rate": hr,
        "spo2": spo2,
        "status": status
    }
    data_store.append(entry)
    
    if len(data_store) > MAX_SIZE:
        data_store.pop(0)  # Remove oldest entry if memory exceeds limit
    
    return timestamp  # Return timestamp for app.py use

def get_all_readings():
    """
    Return all stored readings
    """
    return data_store