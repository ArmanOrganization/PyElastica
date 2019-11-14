__doc__ = """ Boundary conditions for rod """

import numpy as np
from elastica._rotations import _get_rotation_matrix


class FreeRod:
    """
    the base class for rod boundary conditions
    also the free rod class
    """

    def __init__(self):
        pass

    def constrain_values(self, rod, time):
        pass

    def constrain_rates(self, rod, time):
        pass


class OneEndFixedRod(FreeRod):
    """
    the end of the rod fixed x[0]
    """

    def __init__(self, fixed_position, fixed_directors):
        FreeRod.__init__(self)
        self.fixed_position = fixed_position
        self.fixed_directors = fixed_directors

    def constrain_values(self, rod, time):
        rod.position[..., 0] = self.fixed_position
        rod.directors[..., 0] = self.fixed_directors

    def constrain_rates(self, rod, time):
        rod.velocity[..., 0] = 0.0
        rod.omega[..., 0] = 0.0


class HelicalBucklingBC(FreeRod):
    """
    boundary condition for helical buckling
    controlled twisting of the ends
    """

    def __init__(self, position, director, twisting_time, slack, number_of_rotations):
        FreeRod.__init__(self)
        self.twisting_time = twisting_time

        angel_vel_scalar = (
            2.0 * number_of_rotations * np.pi / self.twisting_time
        ) / 2.0
        shrink_vel_scalar = slack / (self.twisting_time * 2.0)

        direction = (position[1] - position[0]) / np.linalg.norm(
            position[1] - position[0]
        )

        self.final_start_position = position[0] + slack / 2.0 * direction
        self.final_end_position = position[1] - slack / 2.0 * direction

        self.ang_vel = angel_vel_scalar * direction
        self.shrink_vel = shrink_vel_scalar * direction

        theta = number_of_rotations * np.pi

        self.final_start_directors = (
            _get_rotation_matrix(theta, direction.reshape(3, 1)).reshape(3, 3)
            @ director[..., 0]
        )  # rotation_matrix wants vectors 3,1
        self.final_end_directors = (
            _get_rotation_matrix(-theta, direction.reshape(3, 1)).reshape(3, 3)
            @ director[..., 1]
        )  # rotation_matrix wants vectors 3,1

    def constrain_values(self, rod, time):
        if time > self.twisting_time:
            rod.position[..., 0] = self.final_start_position
            rod.position[..., -1] = self.final_end_position

            rod.directors[..., 0] = self.final_start_directors
            rod.directors[..., -1] = self.final_end_directors

    def constrain_rates(self, rod, time):
        if time > self.twisting_time:
            rod.velocity[..., 0] = 0.0
            rod.omega[..., 0] = 0.0

            rod.velocity[..., -1] = 0.0
            rod.omega[..., -1] = 0.0

        else:
            rod.velocity[..., 0] = self.shrink_vel
            rod.omega[..., 0] = self.ang_vel

            rod.velocity[..., -1] = -self.shrink_vel
            rod.omega[..., -1] = -self.ang_vel
