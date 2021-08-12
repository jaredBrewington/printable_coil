import test_pymesh.make_cylindrical_shell as shell
import pymesh
from time import time


def get_cyl_shell_mesh():
    # coil parameters
    inner_radius = 0.035
    outer_radius = 0.0455  #  larger than outer wire radius so grooves have good depth
    length = 0.52475 - 0.225

    coil_position = 0.225  # desired location of coil endcap (side with smaller x)
    translation_distance = length / 2 + coil_position

    # make cylindrical shell
    cyl_shell = shell.get_tube_mesh(
        length=length, inner_radius=inner_radius, outer_radius=outer_radius
    )
    # rotate and translate cylinder to be in the wires location
    cyl_shell = shell.get_rotated_shell_along_x(cyl_shell)
    cyl_shell = shell.get_translated_mesh(cyl_shell, translation_distance)

    return cyl_shell


def main():
    start_time = time()

    cyl_shell = get_cyl_shell_mesh()
    # load wires mesh from obj
    wire_mesh_file = "multi_wire.obj"
    multi_wire_mesh = pymesh.load_mesh(wire_mesh_file)
    # remove multi_wire_mesh from cyl_shell to make grooves
    print(
        "Removing grooves in file '{}' from cylindrical shell...".format(wire_mesh_file)
    )
    output_mesh = pymesh.boolean(cyl_shell, multi_wire_mesh, operation="difference")
    # save coil to file
    output_file = "printable_coil.obj"
    pymesh.save_mesh(output_file, output_mesh)

    print("Finished in {} minutes".format((time() - start_time) / 60))


if __name__ == "__main__":
    main()
