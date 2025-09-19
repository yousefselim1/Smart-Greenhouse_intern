# Smart-Greenhouse_intern 🌱

IoT-enabled Smart Greenhouse system integrating **Raspberry Pi, Arduino, and Python** with a Flask web interface.

---

## 🚀 Features
- **Sensor Integration**: Reads temperature, humidity, soil moisture.
- **Actuator Control**: Automates fans, pumps, and heaters.
- **Flask Web App**:
  - `app.py` backend with routes.
  - `templates/index.html` dashboard for real-time monitoring.
- **Data Processing**: `smart_greenhouse.py` handles sensor-actuator logic.
- **Requirements**: all Python dependencies in `requirements.txt`.

---

## 📂 Project Structure
SMART_GREENHOUSE_WEB/
│── app.py # Flask server
│── smart_greenhouse.py # core IoT logic
│── requirements.txt # dependencies
│── templates/
│ └── index.html # web dashboard
│── pycache/ # (ignored)



---

## ⚙️ Installation
```bash
# clone repo
git clone https://github.com/yousefselim1/Smart-Greenhouse_intern.git
cd Smart-Greenhouse_intern

# setup virtual environment
python -m venv .venv
.venv\Scripts\activate   # Windows
# source .venv/bin/activate  # Linux/Mac

# install dependencies
pip install -r requirements.txt



🔧 Hardware Used

Raspberry Pi (gateway + Flask server)

Arduino (sensor/actuator control)

DHT11/DHT22 (temperature & humidity)

Soil moisture sensor

Relay modules for pumps/fans

📊 Future Work

Add predictive AI models for environment control.

Deploy with Docker.

Expand dashboard with charts and logs.