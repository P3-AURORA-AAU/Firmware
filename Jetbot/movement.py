from flask import Flask, request, jsonify
from jetbot import Robot
from BMI160_i2c import Driver
from time import sleep

# ----------------------------
# Initialize IMU
# ----------------------------
sensor = Driver(0x68)
robot = Robot()
robot.stop()
app = Flask(__name__)
# IMPORTANT: do calibration ONLY when device is still and flat
sensor.setAccelOffsetEnabled(True)

# Flat on table, Z axis up
sensor.autoCalibrateXAccelOffset(0)
sensor.autoCalibrateYAccelOffset(0)
sensor.autoCalibrateZAccelOffset(1)

sleep(0.1)  # let offsets settle

# ----------------------------
# Movement class
# ----------------------------
class Move:
    @staticmethod
    def stop():
        print("[MOVE] stop")
        robot.stop()

    @staticmethod
    def move_forward():
        print("[MOVE] forward")
        robot.set_motors(0.2, 0.19)
        sleep(0.72)
        robot.stop()

    @staticmethod
    def move_backward():
        print("[MOVE] backward")
        robot.set_motors(-0.2, -0.19)
        sleep(0.52)
        robot.stop()

    @staticmethod
    def move_right():
        print("[MOVE] left")
        robot.set_motors(0.105, -0.1)
        sleep(0.86)
        robot.stop()
        

    @staticmethod
    def move_left():
        print("[MOVE] right")
        robot.set_motors(-0.105, 0.1)
        sleep(0.86)
        robot.stop()

    @staticmethod
    def f_moving_left():
        print("[MOVE] moving left")
        robot.set_motors(0.2, 0.4)

    @staticmethod
    def f_moving_right():
        print("[MOVE] moving right")
        robot.set_motors(0.4, 0.2)
    @staticmethod
    def b_moving_left():
        print("[MOVE] moving left")
        robot.set_motors(-0.2, -0.4)

    @staticmethod
    def b_moving_right():
        print("[MOVE] moving right")
        robot.set_motors(-0.4, -0.2)

# ----------------------------
# IMU class
# ----------------------------
class IMU:
    # If driver returns raw values
    ACCEL_SCALE = 16384.0  # ±2g
    G = 9.80665

    @staticmethod
    def collect():
        print("sending imu data")
        gx, gy, gz, ax, ay, az = sensor.getMotion6()

        # Convert raw accel → m/s²
        ax = (ax / IMU.ACCEL_SCALE) * IMU.G
        ay = (ay / IMU.ACCEL_SCALE) * IMU.G
        az = (az / IMU.ACCEL_SCALE) * IMU.G

        return { "gx": gx, "gy": gy, "gz": gz, "ax": ax, "ay": ay, "az": az,}



# Map movement actions
MOVE_ACTIONS = {
    "none": Move.stop,
    "forward": Move.move_forward,
    "backwards": Move.move_backward,
    "left": Move.move_left,
    "right": Move.move_right,
    "forward_left": Move.f_moving_left,
    "forward_right": Move.f_moving_right,
    "backwards_left": Move.b_moving_left,
    "backwards_right": Move.b_moving_right,
}

# ----------------------------
# Movement endpoint
# ----------------------------
@app.route("/move/<action>", methods=["POST"])
def move_endpoint(action):
    fn = MOVE_ACTIONS.get(action)
    if not fn:
        return jsonify({"ok": False, "error": f"Unknown action '{action}'"}), 404
    try:
        fn()
        return jsonify({"ok": True, "action": action})
    except Exception as e:
        robot.stop()
        return jsonify({"ok": False, "error": str(e)}), 500

# ----------------------------
# IMU endpoint
# ----------------------------
@app.route("/imu/collect", methods=["POST"])
def imu_endpoint():
    try:
        return jsonify({"ok": True, "data": IMU.collect()})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

# ----------------------------
# Shutdown endpoint
# ----------------------------
@app.route("/shutdown", methods=["POST"])
def shutdown_endpoint():
    robot.stop()
    return jsonify({"ok": True})

# ----------------------------
# Test endpoint
# ----------------------------
@app.route("/test", methods=["POST"])
def test_endpoint():
    robot.set_motors(0.0, 0.19)
    sleep(0.8)
    robot.stop()
        
    robot.set_motors(0.195, 0.0)
    sleep(0.8)
    robot.stop()
    return jsonify({"ok": True})
    


# ----------------------------
# Run server in Jupyter
# ----------------------------

import threading

def run_flask():
    # use_reloader=False is important to avoid Flask restarting
    app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False, threaded=True)
    print("[server] is up")

# Run Flask in a separate daemon thread
flask_thread = threading.Thread(target=run_flask, daemon=True)
flask_thread.start()

