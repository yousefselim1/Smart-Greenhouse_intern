from flask import Flask, jsonify, render_template, request
from smart_greenhouse import SmartGreenhouse
import time, socket, json, os

CONFIG_FILE = "sensor_config.json"

def load_config():
    if not os.path.exists(CONFIG_FILE):
        default_cfg = {
            "use_mock_data": False,
            "mock_values": {
                "time":3,
                "temperature": 25.0,
                "soil_moisture": 400,
                "humidity": 50.0
            }
        }
        with open(CONFIG_FILE, "w") as f:
            json.dump(default_cfg, f, indent=4)
        return default_cfg
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)

def save_config(cfg):
    with open(CONFIG_FILE, "w") as f:
        json.dump(cfg, f, indent=4)

app = Flask(__name__)
greenhouse = SmartGreenhouse()

ARDUINO_PORT = "/dev/ttyACM0"  # Change if needed

def connect_and_do(action_func):
    cfg = load_config()
    if cfg.get("use_mock_data"):
        return action_func(None, mock_data=cfg["mock_values"])
    
    # Otherwise connect to Arduino
    port_name = ARDUINO_PORT
    if not greenhouse.connect(port_name):
        return {"error": f"Failed to connect to Arduino on {port_name}"}, 500
    time.sleep(2)
    try:
        return action_func(greenhouse)
    finally:
        greenhouse.disconnect()

@app.route("/")
def index():
    return render_template("index.html", sensors=['temperature', 'soil_moisture', 'humidity'])

# Get all sensors
@app.route("/api/sensors")
def get_all_sensors():
    def action(gh, mock_data=None):
        if mock_data:
            return jsonify(mock_data)
        return jsonify(gh.read_sensors())
    return connect_and_do(action)

# Get one sensor by name
@app.route("/api/sensor/<name>")
def get_sensor(name):
    def action(gh, mock_data=None):
        if mock_data:
            if name in mock_data:
                return jsonify({name: mock_data[name]})
            return jsonify({"error": "Sensor not found"}), 404
        data = gh.read_sensors()
        if name in data:
            return jsonify({name: data[name]})
        return jsonify({"error": "Sensor not found"}), 404
    return connect_and_do(action)

# Do actuator action
@app.route("/api/action/<act>")
def do_action(act):
    def action(gh, mock_data=None):
        if mock_data:
            return jsonify({"error": "Cannot control actuators in mock mode"}), 400
        actions = {
            "fanon1": lambda: gh.fanon(1),
            "fanoff1": lambda: gh.fanoff(1),
            "fanon2": lambda: gh.fanon(2),
            "fanoff2": lambda: gh.fanoff(2),
            "pumpon": gh.pumpon,
            "pumpoff": gh.pumpoff,
            "heateron": gh.heateron,
            "heateroff": gh.heateroff
        }
        if act in actions:
            actions[act]()
            return jsonify(gh.read_sensors())
        return jsonify({"error": "Unknown action"}), 400
    return connect_and_do(action)




# Change mock mode from API
@app.route("/api/config", methods=["POST"])
def set_mock_mode():

    mock_value = request.args.get("mock")

    if mock_value is None:
        return jsonify({"error": "Please provide ?mock=true or ?mock=false"}), 400
    
    cfg = load_config()
    if mock_value.lower() in ["true", "1", "yes"]:
        cfg["use_mock_data"] = True

    elif mock_value.lower() in ["false", "0", "no"]:
        cfg["use_mock_data"] = False

    else:
        return jsonify({"error": "Invalid value for mock"}), 400
    
    save_config(cfg)
    return jsonify({"message": "Configuration updated", "use_mock_data": cfg["use_mock_data"]})



if __name__ == "__main__":
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    print(f"Server running on http://{local_ip}:5000")
    app.run(host="0.0.0.0", port=5000)







