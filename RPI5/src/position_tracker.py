import numpy as np

class PositionTracker:
    def __init__(self, grid_cell_size):
        self.position = np.array([0.0, 0.0])
        self.velocity = np.array([0.0, 0.0])
        self.orientation = 0.0 # this is in radians btw and not degrees, cus python hates degrees or something
        self.last_time = None
        self.grid_scale = grid_cell_size # in meters

    # update position based on arduino readings using... math (scary stuff)
    #   the specific concept is called "dead reckoning", read more here: https://www.rfwireless-world.com/articles/dead-reckoning-navigation-method
    # acceleration_x/y is the acceleration (no way) in m/s
    # gyro_z is the angular velocity in radians/s
    # dt is how much time has passed since last
    def update(self, acceleration_x, acceleration_y, gyro_z, dt):
        # calculate the direction the rover is now facing
        self.orientation += gyro_z * dt
        self.orientation = self.orientation % (2 * np.pi) # normalize

        # rotation matrix jumpscare (only 2 axis tho as our robot is unable to fly)
        #   https://ocw.mit.edu/courses/2-017j-design-of-electromechanical-robotic-systems-fall-2009/0da9fb3965410fd50979bb179b56805a_MIT2_017JF09_ch09.pdf
        cos_val = np.cos(self.orientation)
        sin_val = np.sin(self.orientation)

        # convert from robot perspective to global/room perspective using cool matrix transformations (this is literally one of our workshop things lol)
        acceleration_global_x = acceleration_x * cos_val - acceleration_y * sin_val
        acceleration_global_y = acceleration_x * sin_val + acceleration_y * cos_val

        # update velocity based on acceleration
        self.velocity[0] += acceleration_global_x * dt
        self.velocity[1] += acceleration_global_y * dt

        # update position based on velocity
        self.position[0] += self.velocity[0] * dt
        self.position[1] += self.velocity[1] * dt

        # convert to grid coordinates
        grid_x = int(self.position[0] / self.grid_scale)
        grid_y = int(self.position[1] / self.grid_scale)

        return [grid_x, grid_y]