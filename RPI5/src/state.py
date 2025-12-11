from pathfinding.a_star import a_star_search
import asyncio

class RoverState:
    def __init__(self):
        # test map, idk put this somewhere else mayb
        self.obj_grid = [
            [0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 1, 1, 0, 0, 0],
            [0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 1, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        ]

        self.current_position = [0, 0]
        self.destination = [7, 14]
        self.current_path = None
        self.obj_theshold = 0 # we only have one type of obstacle so yea, just keep this 0 (for some reason the threshold value is one below the one u actually want)

        self.on_path_update = None # call when path is updated, we set this in the main function so we can send stuff over ws

        # add other state stuff, we probably want more stuff than just pathfinding here
        self.speed = "100%"

    # recalculate the path with a*
    def recalculate_path(self):
        print(f"[State] Recalculate path from {self.current_position} to {self.destination}")

        path = a_star_search(
            self.obj_grid,
            self.current_position,
            self.destination,
            self.obj_theshold,
        )

        if path is None:
            print("[State] No path found, initiating self-destruct...")
            return

        self.current_path = path
        print("[State] Path found")
        if self.on_path_update:
            asyncio.create_task(self.on_path_update({
                "type": "path_data",
                "data": {
                    "grid": self.obj_grid,
                    "path": [[p[0], p[1]] for p in path],  # convert tuples to lists cus json
                    "start": self.current_position,
                    "destination": self.destination
                }
            }))

    # set a new destination and recalculate path
    def set_destination(self, destination):
        self.destination = destination
        self.recalculate_path()
        print(f"[State] Set new destination: {destination}")

    # update rover position
    def update_position(self, new_position):
        self.current_position = new_position
        self.recalculate_path()
        print(f"[State] Updated position: {self.current_position}")

    def set_speed(self, speed):
        self.speed = speed
        print(f"[State] Set speed: {self.speed}")

    # update the grid, probably wont use this in the POC, but erm now its here ig
    def update_grid(self, new_grid):
        self.obj_grid = new_grid
        self.recalculate_path()

# global state waow i <3 singleton design pattern
rover_state = RoverState()