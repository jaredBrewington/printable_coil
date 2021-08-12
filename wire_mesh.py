from numpy.core.numeric import cross
import pymesh
from wire import Wire
import numpy as np


class WireMesh:
    """Class for generating mesh for wires wound onto cylindrical shell aligned with x-axis

    The mesh generated will be closed, even if the input wire is not a closed loop
    """

    def __init__(self, wire: Wire):
        self.wire = wire
        # wire mesh cross section dimensions--depends on the gauge wire you want to use
        self.width = 0.0017  # tangent to the surface
        self.height = 0.0017  # normal to the surface
        # get vertices and faces to make mesh
        self.vertices = self.get_vertices()
        self.faces = self.get_faces()
        # using pymesh to create the mesh
        self.mesh = pymesh.form_mesh(self.vertices, self.faces)

    def get_normal_vec(self, indx):
        """Gives the unit vector normal to the surface of the cylindrical shell

        The normal vector corresponds to the wire point (x,y,z) at index = indx
        If you want to wrap wires on a different shape (not cylindical shell),
        this function will need to be changed

        Args:
            indx (int): index of wire point at which surface normal is calculated

        Returns:
            [type]: [description]
        """
        # need to know coil endcap locations and inner/outer radius
        # this is assuming cyl axis is x axis--otherwise y and z will need to be offset
        all_x, all_y, all_z = self.wire.points
        max_x = np.amax(all_x)
        min_x = np.amin(all_x)
        max_radius = np.amax(np.sqrt(all_y * all_y + all_z * all_z))
        min_radius = np.amin(np.sqrt(all_y * all_y + all_z * all_z))

        x, y, z = self.wire.points[
            :, indx
        ]  # might change this to interpolation later so indx need not be an int
        error_bar = 5e-4  # 0.1 mm

        # is point on positive/negative endcap?
        is_pos_end = abs(x - max_x) < error_bar
        is_neg_end = abs(x - min_x) < error_bar
        # is point on outer/inner radius?
        is_out_rad = (np.sqrt(y * y + z * z) - max_radius) < error_bar
        is_in_rad = (np.sqrt(y * y + z * z) - min_radius) < error_bar

        normal_vec = np.zeros(3)
        phi = np.arctan2(z, y)  # angle of (x,y,z) vector in yz-plane

        if is_out_rad:
            normal_vec[1] = np.cos(phi)
            normal_vec[2] = np.sin(phi)
        elif is_in_rad:
            normal_vec[1] = -np.cos(phi)
            normal_vec[2] = -np.sin(phi)
        if is_pos_end:
            normal_vec[0] = 1
        elif is_neg_end:
            normal_vec[0] = -1

        # if point is near corner (at endcap and the inner or outer radius), angle normal will be at 45 degrees

        return normal_vec / np.linalg.norm(normal_vec)

    def get_tangential_vec(self, indx):
        """Gives vector pointing in direction of the wire at wire point indx

        Args:
            indx (int): index of wire point at which wire direction is calculated

        Returns:
            np.ndarray: (x,y,z) unit vector of wire direction
        """
        tangential_vec = self.wire.interp.derivative_direction(indx)
        return tangential_vec

    def get_vertices(self):
        """Gives the mesh vertices at each wire point

        Returns:
            np.ndarray: array of vertices--shape = (num_of_vertices, 3)
        """
        # vertex parameters
        num_vertices_per_point = 4  # 4 gives rectangular shape
        rect_width = self.width
        rect_height = self.height
        num_unique_points = self.wire.points.shape[1]
        # first point is same as last--prevent repeat vertices
        if self.wire.is_closed:
            num_unique_points -= 1

        num_vertices = num_unique_points * num_vertices_per_point
        vertices = np.zeros((num_vertices, 3))
        # set vertex data
        for i in range(num_unique_points):
            j = i * num_vertices_per_point
            # one vector for rectangle plane--center to height
            normal_vec = self.get_normal_vec(i)
            along_curve_vec = self.get_tangential_vec(i)
            # other vector for rectangle plane--center to width
            cross_vec = np.cross(along_curve_vec, normal_vec)
            cross_vec /= np.linalg.norm(cross_vec)  # normalize
            # scale vectors to groove size
            normal_vec *= rect_height / 2
            cross_vec *= rect_width / 2

            # debug
            if normal_vec[0] > 0.99:
                print("Normal vec is in pos x direciton \n cross_vec is ", cross_vec)
                input()

            x, y, z = np.transpose(self.wire.points)[i]
            # add or subtract vectors to point from x,y,z to proper vertex
            # the order is important for properly defining the faces later
            vertex_0 = np.array(
                [
                    x + cross_vec[0] + normal_vec[0],
                    y + cross_vec[1] + normal_vec[1],
                    z + cross_vec[2] + normal_vec[2],
                ]
            )
            vertex_1 = np.array(
                [
                    x - cross_vec[0] + normal_vec[0],
                    y - cross_vec[1] + normal_vec[1],
                    z - cross_vec[2] + normal_vec[2],
                ]
            )
            vertex_2 = np.array(
                [
                    x - cross_vec[0] - normal_vec[0],
                    y - cross_vec[1] - normal_vec[1],
                    z - cross_vec[2] - normal_vec[2],
                ]
            )
            vertex_3 = np.array(
                [
                    x + cross_vec[0] - normal_vec[0],
                    y + cross_vec[1] - normal_vec[1],
                    z + cross_vec[2] - normal_vec[2],
                ]
            )

            vertices[j] = vertex_0
            vertices[j + 1] = vertex_1
            vertices[j + 2] = vertex_2
            vertices[j + 3] = vertex_3

        return vertices

    def get_faces(self):
        """Gives an array of vertex labels specifying all triangles (faces) in the mesh

        Returns:
            numpy.ndarray: array of ints representing triangles of mesh--shape (num_of_faces, 3)
        """
        # assuming num_vertices_per_point = 4 (rectangles)
        num_verts_per_point = 4
        num_faces_per_connection = 8  # 8 triangle faces to connect 2 rectangles
        # N points gives N-1 connections to make
        num_connections = self.wire.points.shape[1] - 1
        num_faces = num_faces_per_connection * num_connections
        faces = np.zeros((num_faces, 3), dtype=np.int16)  # 3 vertices per traingle

        for i in range(num_connections):
            k = i * num_verts_per_point
            k_next = k + num_verts_per_point
            # pattern for points
            for j in range(num_verts_per_point):
                # 2 faces per side of rectangle
                face_index = (j + k) * 2
                # j + 1 makes vertices go to the next square on last iter of for loop
                j_plus_1 = (j + 1) % num_verts_per_point
                faces[face_index] = [j + k, j + k_next, j_plus_1 + k_next]
                faces[face_index + 1] = [j + k, j_plus_1 + k_next, j_plus_1 + k]

        # if it is an open wire, close mesh at start/end point
        closing_faces = np.zeros((num_verts_per_point, 3))  # 3 is for triangles
        if not self.wire.is_closed:
            # close start face
            closing_faces[0] = np.array([0, 1, 2])
            closing_faces[1] = np.array([0, 3, 2])
            # close end face
            total_verts = self.vertices.shape[0]
            closing_faces[2] = np.array([-4, -3, -2]) + total_verts
            closing_faces[3] = np.array([-4, -1, -2]) + total_verts

            faces = np.append(faces, closing_faces, axis=0)

        # last 8 faces need indices of first 4 vertices...otherwise index will extend above the max vertex index
        faces = faces % (self.vertices.shape[0])

        return faces

    def save_mesh(self, file_name):
        """Write vertices and faces to file in obj format

        Args:
            file_name (str): file location to save mesh
        """
        # pymesh.save_mesh(file_name, self.mesh)
        with open(file_name, "w") as f_out:
            for vertex in self.vertices:
                f_out.write("v")
                for point in vertex:
                    f_out.write(" {}".format(point))
                f_out.write("\n")

            for face in self.faces:
                f_out.write("f")
                for i in face:
                    f_out.write(
                        " {}".format(i + 1)
                    )  # add 1 because obj index starts at 1, not 0
                f_out.write("\n")
