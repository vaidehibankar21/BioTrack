import serial
import time

arduino = serial.Serial('COM3',9600, timeout=1)
time.sleep(2)

print("START")

while True:
    data = arduino.readline().decode().strip()
    print("DATA:", data)