import state
from state import rover_state
from queues import queues

# TODO: make ts actually do stuff
def handle_move(data):
    # "forward" | "backwards" | "left" | "right" | "forward_left" | "forward_right" | "backwards_left" | "backwards_right" | "none"
    print(f"Move: {data["direction"]}")

    direction_message = {
        "type": "move",
        "data": {
            "forward": 0,
            "backward": 0,
            "left": 0,
            "right": 0,
            "speed": state.rover_state.speed,
        }
    }

    # what the fuck
    match data["direction"]:
        case "forward":
            direction_message["data"]["forward"] = 1
        case "backwards":
            direction_message["data"]["backwards"] = 1
        case "left":
            direction_message["data"]["left"] = 1
        case "right":
            direction_message["data"]["right"] = 1
        case "forward_left":
            direction_message["data"]["forward"] = 1
            direction_message["data"]["left"] = 1
        case "forward_right":
            direction_message["data"]["forward"] = 1
            direction_message["data"]["right"] = 1
        case "backward_left":
            direction_message["data"]["backward"] = 1
            direction_message["data"]["left"] = 1
        case "backward_right":
            direction_message["data"]["backward"] = 1
            direction_message["data"]["right"] = 1

    queues.jetbot_send_queue.put_nowait(direction_message)


def handle_speed(data):
    rover_state.set_speed(data["speed"])


def handle_sensor(data):
    # these dont do shit rn lol
    print(f"Sensor: {data}")
