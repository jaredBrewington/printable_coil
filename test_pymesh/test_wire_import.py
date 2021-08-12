import pymesh
import numpy as np
from glob import glob
import os
import random

from pymesh.wires.WireNetwork import WireNetwork

def line_to_groove(wire_network:WireNetwork):
    inflator = pymesh.wires.Inflator(wire_network)
    inflator.inflate(1)
    inflator.set_profile(4)
    return inflator

def get_wire_reduce_edges(wire_network:WireNetwork, tolerance = 1):
    # reduce number of edges by making minimum spacing between points 1 mm
    # need something like if dist < tol, change edge to skip that number----- [1,2],[2,3] --> [1,3]  OR delete vertex 2 and delete the last edge would work the same
    i = 0
    new_network = wire_network
    while i < new_network.num_edges - 1:
        print(f"i = {i}, num_edges = {new_network.num_edges}")
        print(f"wire length[i] = {new_network.wire_lengths[i]}")
        distance = new_network.wire_lengths[i]
        if distance >= tolerance:
            i += 1
            continue

        vertices = np.delete(new_network.vertices, i+1)
        edges = np.delete(new_network.edges, -1, axis=0)
        edges[-1,1] = 0
        new_network = pymesh.wires.WireNetwork.create_from_data(vertices, edges)

    return wire_network

def get_wire_mesh(wire_file):
    print(wire_file)
    vertices = np.loadtxt(wire_file) [::5]
    vertices = vertices*1000
    edges = np.array([[p1,p1+1] for p1 in range(len(vertices))])
    edges[-1, 1] = 0

    wire_network = pymesh.wires.WireNetwork.create_from_data(vertices, edges)
    

    try:
        inflator = line_to_groove(wire_network)
    except RuntimeError as e:
        wire_newtwork = get_wire_reduce_edges(wire_network)
        inflator = line_to_groove(wire_network)

    return inflator.mesh

def main():

    wire_folder = "/Users/jared/Desktop/spinTransWires/doubleCoil/coil1/wires"
    wire_file_list = sorted([os.path.join(wire_folder, file_name) for file_name in os.listdir(wire_folder)])

    output_mesh = get_wire_mesh(wire_file_list[20])

    for wire_file in wire_file_list[25:30]:
        print(os.path.basename(wire_file))
        temp_mesh = get_wire_mesh(wire_file)
        output_mesh = pymesh.boolean(output_mesh, temp_mesh, operation="union")

    if output_mesh:
        output_file = "wire_test.obj"
        pymesh.save_mesh(output_file, output_mesh)


if __name__=="__main__":
    main()