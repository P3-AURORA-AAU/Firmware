from state import rover_state
import requests

MOVE_ACTIONS = {
    "none": "stop",
    "forward": "forward",
    "backwards": "backward",
    "left": "left",
    "right": "right",
    "forward_left": "forward_left",
    "forward_right": "forward_right",
    "backwards_left": "backward_left",
    "backwards_right": "backward_right",
}
MOVEMENT_URL = "http://10.42.7.85:5000/move" # POST movement


# TODO: make ts actually do stuff
def handle_move(data):
    # "forward" | "backwards" | "left" | "right" | "forward_left" | "forward_right" | "backwards_left" | "backwards_right" | "none"
    print(f"Move: {data['direction']}")

    # simulate movement for testing
    #curr = rover_state.current_position

    #match data["direction"]:
    #    case "forward":
    #        rover_state.update_position([curr[0] - 1, curr[1]])
    #    case "backwards":
    #        rover_state.update_position([curr[0] + 1, curr[1]])
    #    case "left":
    #        rover_state.update_position([curr[0], curr[1] - 1])
    #    case "right":
    #        rover_state.update_position([curr[0], curr[1] + 1])

    direction = data.get("direction")
    """
    if direction == "forward":
        rover_state.update_position([curr[0] - 1, curr[1]])
    
    elif direction == "backwards":
        rover_state.update_position([curr[0] + 1, curr[1]])
    
    elif direction == "left":
        rover_state.update_position([curr[0], curr[1] - 1])
    
    elif direction == "right":
        rover_state.update_position([curr[0], curr[1] + 1])
    
    else:
        print(f"[rover] Unknown direction: {direction}")
    """
    send_movement_command_blocking(direction)


def handle_speed(data):
    rover_state.set_speed(data["speed"])


def handle_sensor(data):
    # these dont do shit rn lol
    print(f"Sensor: {data}")

def send_movement_command_blocking(action: str): 
    if action not in MOVE_ACTIONS: 
        print(f"[Movement] Invalid action: {action}") 
        return 

    url = f"{MOVEMENT_URL}/{action}" # POST /move/<action> 
    try: 
        response = requests.post(url, timeout=1) 
        response.raise_for_status() 
        print(f"[Movement] Sent action '{action}', response: {response.text}") 
    except Exception as e: 
        print(f"[Movement] Failed to send action '{action}': {e}")
