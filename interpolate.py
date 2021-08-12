from scipy.interpolate import InterpolatedUnivariateSpline as IUS
import numpy as np


class Interpolate_3d:
    """ A class used for interpolating a list of 3D points into a parametric curve

        The parameter defining the curve is the index of the input points array.
        Using scipy.interpolate.InterpolatedUnivariateSpline to do interpolation
    """

    def __init__(self, data):
        """ 
        Args:
            data (np.ndarray): points to interpolate--shape = (3, num_points)
        """
        self.x = data[0]
        self.y = data[1]
        self.z = data[2]
        # all axes should have the same number of points for interpolation
        assert len(self.x) == len(self.y) and len(self.x) == len(self.z)

        # make interpolation using a parameter to define the 3D path as a parametric curve
        self._parameter = np.arange(len(self.x))
        self.interp_x = IUS(self._parameter, self.x)
        self.interp_y = IUS(self._parameter, self.y)
        self.interp_z = IUS(self._parameter, self.z)

    def interpolate(self, t_parametric):
        """Gives the (x,y,z) coord corresponding to the parametric value

        Args:
            t_parametric (float): value of parameter which defines the parametric interpolation curve

        Returns:
            np.ndarray: (x,y,z) coord
        """
        interpolated_point = np.zeros(3)
        interpolated_point[0] = self.interp_x(t_parametric)
        interpolated_point[1] = self.interp_y(t_parametric)
        interpolated_point[2] = self.interp_z(t_parametric)

        return interpolated_point

    def derivative_direction(self, t_parametric):
        """Returns derivative direction using linear estimate of derivative

        Uses a point at t-dt and a point at t+dt along the curve, then puts dx, dy, dz into a normalized vector
        which points in the direction of change of the parametric curve

        Args:
            t_parametric (float): value of parameter which defines the parametric interpolation curve

        Returns:
            np.ndarray: (dx, dy, dz) unit vector pointing in direction of slope
        """
        dt_step = 1e-1
        t_lower = t_parametric - dt_step
        t_upper = t_parametric + dt_step
        point_lower = self.interpolate(t_lower)
        point_upper = self.interpolate(t_upper)

        deriv_vector = point_upper - point_lower
        normalized_deriv_vector = deriv_vector / np.linalg.norm(deriv_vector)

        return normalized_deriv_vector
