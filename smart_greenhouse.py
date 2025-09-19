import serial
import serial.tools.list_ports
import threading
import time
import pickle
import os
import numpy as np
from sklearn.linear_model import LogisticRegression

class SmartGreenhouse:
    def __init__(self, baudrate=9600):
        self.arduino = None
        self.connected = False
        self.stop_thread = False
        self.thread = None
        self.baudrate = baudrate
        self.sensor_data = {
            'temperature': 0.0,
            'soil_moisture': 0.0,
            'humidity': 0.0,
            'last_update': None
        }
        self.actuator_states = {
            'fan1': False,
            'fan2': False,
            'pump': False,
            'heater': False
        }

    def list_ports(self):
        return [{'port': p.device, 'description': p.description}
                for p in serial.tools.list_ports.comports()]

    def connect(self, port):
        if self.connected:
            self.disconnect()
        try:
            self.arduino = serial.Serial(port, self.baudrate, timeout=1)
            time.sleep(2)
            self.connected = True
            self.stop_thread = False
            self.thread = threading.Thread(target=self._read_loop)
            self.thread.daemon = True
            self.thread.start()
            return True
        except Exception as e:
            print(f"Connection failed: {e}")
            self.connected = False
            return False

    def disconnect(self):
        if not self.connected:
            return False
        try:
            self.stop_thread = True
            if self.thread and self.thread.is_alive():
                self.thread.join(timeout=2)
            if self.arduino:
                self.arduino.close()
            self.connected = False
            self.arduino = None
            return True
        except Exception as e:
            print(f"Disconnect error: {e}")
            return False

    def _read_loop(self):
        while self.connected and not self.stop_thread:
            try:
                self.arduino.write(b'R\n')
                time.sleep(0.5)
                if self.arduino.in_waiting > 0:
                    line = self.arduino.readline().decode('utf-8').strip()
                    self._parse_sensor_data(line)
                time.sleep(2)
            except Exception as e:
                print(f"Arduino read error: {e}")
                self.connected = False
                break

    def _parse_sensor_data(self, line):
        try:
            values = line.split(',')
            if len(values) >= 2:
                self.sensor_data['temperature'] = float(values[0])
                self.sensor_data['soil_moisture'] = float(values[1])
                self.sensor_data['humidity'] = self._calculate_humidity(
                    self.sensor_data['soil_moisture'],
                    self.sensor_data['temperature']
                )
                self.sensor_data['last_update'] = time.time()
        except Exception as e:
            print(f"Sensor data parsing error: {e}")

    def _calculate_humidity(self, soil_moisture, temperature):
        base_humidity = 45
        soil_factor = (soil_moisture - 400) / 20
        temp_factor = (temperature - 25) / 2
        humidity = base_humidity - soil_factor + temp_factor
        return round(max(10, min(90, humidity)), 1)

    def _send_command(self, command):
        if self.connected and self.arduino:
            try:
                self.arduino.write((command + '\n').encode())
                return True
            except:
                return False
        return False

    def read_sensors(self):
        return self.sensor_data.copy()


    # Actuator methods
    def fanon(self, n): return self._send_command('0' if n == 1 else '2')
    def fanoff(self, n): return self._send_command('1' if n == 1 else '3')
    def pumpon(self): return self._send_command('6')
    def pumpoff(self): return self._send_command('7')
    def heateron(self): return self._send_command('8')
    def heateroff(self): return self._send_command('9')
