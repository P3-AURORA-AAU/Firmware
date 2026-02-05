from state import rover_state

# TODO: make ts actually do stuff
def handle_move(data):
    # "forward" | "backwards" | "left" | "right" | "forward_left" | "forward_right" | "backwards_left" | "backwards_right" | "none"
    print(f"Move: {data['direction']}")

    # simulate movement for testing
    curr = rover_state.current_position

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



def handle_speed(data):
    rover_state.set_speed(data["speed"])


def handle_sensor(data):
    # these dont do shit rn lol
    print(f"Sensor: {data}")
