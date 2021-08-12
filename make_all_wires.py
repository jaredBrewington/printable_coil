##### use this script to make an obj file of the mesh with all the wires turned into square
##### those squares can be used to cut groove using the boolean operation

from pymesh.meshutils.collapse_short_edges import collapse_short_edges
from wire import Wire
from wire_mesh import WireMesh
import pymesh
from glob import glob
import os
from time import time


def get_wire_mesh(file_path):
    # load wire and turn it into a mesh
    wire = Wire(file_name=file_path)
    wire.close_loop()
    wire_mesh = WireMesh(wire)
    # simplify mesh by reducing edges
    wire_mesh, __ = pymesh.collapse_short_edges(wire_mesh.mesh, rel_threshold=0.05)
    return wire_mesh


def get_union_wire_mesh_and_output_mesh(wire_mesh, output_mesh):
    if output_mesh == None:
        return wire_mesh
    else:
        new_mesh = pymesh.boolean(output_mesh, wire_mesh, operation="union")
        return new_mesh


def main():
    initial_time = time()

    # get all the wires
    coil_folder = "prototype_double_cos_coil/mirror_coil1/wires"
    wire_file_list = [
        os.path.join(coil_folder, f_name) for f_name in os.listdir(coil_folder)
    ]

    # add the mesh of each wire together using the "union" boolean operation
    multi_wire_mesh = None
    total_num = len(wire_file_list)
    count = 0

    for wire_path in wire_file_list:
        # print some info about this iteration
        start_time = time()
        print("{:.2f}% done".format(100 * count / total_num))
        print("Adding mesh for {}".format(os.path.basename(wire_path)))

        wire_mesh = get_wire_mesh(wire_path)

        multi_wire_mesh = get_union_wire_mesh_and_output_mesh(
            wire_mesh, multi_wire_mesh
        )

        count += 1
        print("Took {:.1f} seconds this loop\n".format(time() - start_time))

    # write wires mesh to file
    output_file = "multi_wire.obj"
    pymesh.save_mesh(output_file, multi_wire_mesh)

    print("Total time was {} seconds".format(time() - initial_time))


if __name__ == "__main__":
    main()
