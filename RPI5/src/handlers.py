# handlers.py

from state import RoverState
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

MOVEMENT_URL = "http://10.42.7.85:5000/move"  # POST /move/<action>

# Same ordering you already use in state.py
_DIRECTION_ORDER = ["up", "right", "down", "left"]  # clockwise


def _turn(current: str, action: str) -> str:
    i = _DIRECTION_ORDER.index(current)
    if action == "left":
        return _DIRECTION_ORDER[(i - 1) % 4]
    if action == "right":
        return _DIRECTION_ORDER[(i + 1) % 4]
    return current


def _apply_move_to_state(action: str) -> None:
    """
    Update RoverState using the tracker:
      - left/right: change orientation ONLY (no position change)
      - forward/backwards: move relative to current orientation
      - diagonals: (optional) turn then move
    """
    t = RoverState.tracker  # PositionTracker

    if action in ("none", None):
        return

    # TURN ONLY
    if action in ("left", "right"):
        t.change_direction(_turn(t.direction, action))
        RoverState.current_position = t.position()
        RoverState.recalculate_path()
        print(f"[state] Turned {action}. Now {t}")
        return

    # DIAGONALS (turn then move)
    if action in ("forward_left", "forward_right", "backwards_left", "backwards_right"):
        # turn
        if action.endswith("_left"):
            t.change_direction(_turn(t.direction, "left"))
        else:
            t.change_direction(_turn(t.direction, "right"))

        # move
        if action.startswith("backwards"):
            t.move_back()
        else:
            t.move()

        RoverState.current_position = t.position()
        RoverState.recalculate_path()
        print(f"[state] Diagonal step {action}. Now {t}")
        return

    # MOVE ONLY (relative to orientation)
    if action == "forward":
        t.move()
        RoverState.current_position = t.position()
        RoverState.recalculate_path()
        print(f"[state] Moved forward. Now {t}")
        return

    if action == "backwards":
        t.move_back()
        RoverState.current_position = t.position()
        RoverState.recalculate_path()
        print(f"[state] Moved backwards. Now {t}")
        return

    print(f"[state] Unknown action for state update: {action}")


def handle_move(data):
    """
    Expects:
      data["direction"] in
        "forward" | "backwards" | "left" | "right" |
        "forward_left" | "forward_right" | "backwards_left" | "backwards_right" | "none"
    """
    direction = data.get("direction")
    print(f"Move: {direction}")

    if not direction:
        print("[rover] No direction in move payload")
        return

    send_movement_command_blocking(direction)


def handle_speed(data):
    RoverState.set_speed(data["speed"])


def handle_sensor(data):
    print(f"Sensor: {data}")


def send_movement_command_blocking(action: str):
    """
    Sends the movement command, then updates RoverState (tracker + current_position)
    *after success*, then recalculates the path.
    """
    if action not in MOVE_ACTIONS:
        print(f"[Movement] Invalid action: {action}")
        return

    url = f"{MOVEMENT_URL}/{action}"  # POST /move/<action>

    try:
        response = requests.post(url, timeout=1)
        response.raise_for_status()
        print(f"[Movement] Sent action '{action}', response: {response.text}")

        # Update local state so A* registers the move / turn
        _apply_move_to_state(action)

        # (Optional) if you still want this explicit call, it's already done in _apply_move_to_state:
        # RoverState.recalculate_path()

    except Exception as e:
        print(f"[Movement] Failed to send action '{action}': {e}")

