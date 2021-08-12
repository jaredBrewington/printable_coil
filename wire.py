import numpy as np
from interpolate import Interpolate_3d


class Wire:
    """Loads wire from file OR numpy array into an object that can be refined
    """

    def __init__(self, file_name=None, points=None):
        """
        Args:
            file_name (str, optional): path to file with wire points in x y z columns. Defaults to None.
            points (np.ndarray, optional): x,y,z points--shape=(3, num_of_points). Defaults to None.

        Raises:
            Exception: Input needs to be either np array OR file
        """
        # get data for wire
        if points is not None:
            self.source = "data"
            self.points = np.array(points)
        elif file_name is not None:
            self.source = "file"
            self.points = np.array(self._load_wire_file(file_name))
        else:
            raise Exception(
                "Invalid Wire initialization: need either file or data for wire points"
            )
        # are first and last points the same?
        self.is_closed = np.array_equal(self.points[:, 0], self.points[:, -1])
        # set up interpolation for parametric curve connecting points
        self.t_parametric = np.arange(self.points.shape[1])
        self.interp = Interpolate_3d(self.points)
        self.total_length = self._get_wire_length()

    def _load_wire_file(self, file_name):
        x, y, z = np.loadtxt(file_name, unpack=True)
        return x, y, z

    def _get_wire_length(self):
        sum = 0  # store total length
        prev_point = np.zeros(3)
        next_point = np.zeros(3)
        max_t_param = np.amax(
            self.t_parametric
        )  # t_parametric value of the last wire point
        # take small steps along the curve, summing the spatial distance between consecutive points
        t_param_steps = max_t_param * 1e-4
        for t in np.arange(0, max_t_param + t_param_steps / 2, t_param_steps):
            if t == 0:  # starting point
                prev_point = self.interp.interpolate(t)
                continue

            next_point = self.interp.interpolate(t)
            distance = np.linalg.norm(next_point - prev_point)
            sum += distance
            prev_point = next_point

        return sum

    def _get_next_point_in_sampling(
        self, distance_separation, previous_point, starting_t_param
    ):
        t_param = starting_t_param
        t_param_step = 0.01

        distance = 0
        next_point = np.zeros(3)
        # take small steps in parametric curve until we find a point that is a certain distance away
        while distance < distance_separation:
            t_param += t_param_step
            next_point = self.interp.interpolate(t_param)
            distance = np.linalg.norm(next_point - previous_point)

        return next_point, t_param

    def get_resampled_wire(self, resolution=0.005):
        """Makes a new wire with points separated by distance ~= resolution

        The wire endpoints will remain the same for the resampled wire

        Args:
            resolution (float, optional): approximate distance between sampled wire points. Defaults to 0.005.

        Returns:
            Wire: new Wire object with points interpolated from original wire
        """
        number_of_points = int(self.total_length / resolution)
        new_wire_points = np.zeros((3, number_of_points))

        prev_t_param = 0
        prev_point = self.points[:, 0]
        for i in range(0, number_of_points):
            if i == 0:
                new_wire_points[:, 0] = self.points[:, 0]
                continue
            if i == number_of_points - 1:
                new_wire_points[:, -1] = self.points[:, -1]
                break

            new_wire_points[:, i], new_t_param = self._get_next_point_in_sampling(
                resolution, prev_point, prev_t_param
            )
            prev_point = new_wire_points[:, i]
            prev_t_param = new_t_param

        return Wire(points=new_wire_points)

    def close_loop(self):
        if self.is_closed:
            return
        # add first point to the end of points
        self.points = np.append(self.points, self.points.shape[1], self.points[:, 0])

        # upate wire info
        self.is_closed = True
        # set up interpolation again
        self.t_parametric = np.arange(self.points.shape[1])
        self.interp = Interpolate_3d(self.points)
        self.total_length = self._get_wire_length()
        return
