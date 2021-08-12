from numpy.core.numeric import outer
import pymesh
import numpy as np


def get_tube_mesh(length, inner_radius, outer_radius, num_segments=30):
    """Creates a tube mesh aligned with z-axis and centered at (0,0,0)

    Args:
        length (float): Length of tube 
        inner_radius (float): Inner radius of tube
        outer_radius (float): Outer radius of tube
        num_segments (int, optional): [Number of segments to discretize circles]. Defaults to 30.

    Returns:
        [Mesh]: [Tube shaped mesh]
    """
    mesh = pymesh.generate_tube(
        [0, 0, -length / 2.0],
        [0, 0, length / 2.0],
        outer_radius,
        outer_radius,
        inner_radius,
        inner_radius,
        num_segments,
    )
    return mesh


def get_rotated_shell_along_x(mesh: pymesh.Mesh):
    x, y, z = np.transpose(mesh.vertices)
    phi = np.pi / 2  # 90 deg rotation from z-axis to x-axis
    rotation_matrix = np.array(
        [[np.cos(phi), 0, np.sin(phi)], [0, 1, 0], [-np.sin(phi), 0, np.cos(phi)]]
    )
    new_x = (
        x * rotation_matrix[0, 0]
        + y * rotation_matrix[0, 1]
        + z * rotation_matrix[0, 2]
    )
    new_y = (
        x * rotation_matrix[1, 0]
        + y * rotation_matrix[1, 1]
        + z * rotation_matrix[1, 2]
    )
    new_z = (
        x * rotation_matrix[2, 0]
        + y * rotation_matrix[2, 1]
        + z * rotation_matrix[2, 2]
    )
    vertices = np.transpose(np.array([new_x, new_y, new_z]))
    new_mesh = pymesh.form_mesh(vertices, mesh.faces)
    return new_mesh


def get_translated_mesh(mesh: pymesh.Mesh, distance, axis="x"):
    x, y, z = np.transpose(mesh.vertices)
    if axis == "x":
        x = x + distance
    elif axis == "y":
        x = x + distance
    elif axis == "z":
        x = x + distance
    else:
        Exception("Axis must be 'x', 'y', or 'z'")

    vertices = np.transpose(np.array([x, y, z]))
    new_mesh = pymesh.form_mesh(vertices, mesh.faces)
    return new_mesh


def main():
    # units are meters
    inner_radius = 0.07
    outer_radius = 0.09

    length = 0.30

    tube_mesh = get_tube_mesh(length, inner_radius, outer_radius)
    rot_tube_mesh = get_rotated_shell_along_x(tube_mesh)

    output_file = "test_tube_mesh.obj"
    pymesh.save_mesh(output_file, rot_tube_mesh)


if __name__ == "__main__":
    main()
