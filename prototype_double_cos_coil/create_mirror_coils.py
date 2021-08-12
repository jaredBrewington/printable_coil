import numpy as np
import os
from glob import glob

def rotate_array(arr):
    # need to make sure only first and last points are repeats
    new_arr = np.delete(arr,-1)
    # shift array by certain number of indices
    shift = int(len(new_arr)/4)
    new_arr = np.append(new_arr[shift:], new_arr[:shift])
    # new_arr = np.append(new_arr, new_arr[0]) # close the loop
    return new_arr


def wire_to_file(file_path, x, y, z, rotated=False):
    with open(file_path,"w") as f_out:
        if rotated:
            # don't start coil at the corner so that it loads into SolidWorks better
            x = rotate_array(x)
            y = rotate_array(y)
            z = rotate_array(z)
        for X,Y,Z in zip(x, y, z):
            f_out.write(f"{X} {Y} {Z}\n")

def is_wire_closed(file_name):
    x,y,z = np.loadtxt(file_name, unpack=True)
    if y[0]==0 and y[-1]==0:
        return False
    else:
        return True

def create_closed_wire(x,y,z):
    x_rev, y_rev, z_rev = x[::-1], -1*y[::-1], z[::-1]

    x_full = np.append(x[:-1],x_rev)
    y_full = np.append(y[:-1],y_rev)
    z_full = np.append(z[:-1],z_rev)

    return x_full, y_full, z_full

def create_mirrored_file(coil_name, wire_file_path, is_rotated=True):
    # set up folder and file names
    new_folder = "mirror_" + coil_name
    new_file_path = os.path.join(new_folder, os.path.basename(wire_file_path))
    # load data from wire file
    x,y,z = np.loadtxt(wire_file_path, unpack=True)

    # check if wire is closed loop
    if is_wire_closed(wire_file_path):
        # closed wires are reflected over y=0 to create another closed wire
        new_file_path_mir = os.path.join(new_folder, "mir_"+os.path.basename(wire_file_path))
        x_mir, y_mir, z_mir = x, -1*y, z
        wire_to_file(new_file_path_mir, x_mir, y_mir, z_mir, rotated=is_rotated)   # write mirrored wire to file
    else:
        # open wire loops are mirrored so they are closed
        x,y,z = create_closed_wire(x,y,z)
    # write wire to new folder location
    wire_to_file(new_file_path, x,y,z, rotated=is_rotated)


if __name__ == "__main__":

    coil_folder = "coil1/wires"

    coil_path = os.path.abspath(coil_folder)
    file_list = glob(coil_path + "/wire*.txt")

    for file_name in file_list:
        create_mirrored_file(coil_folder, file_name, is_rotated=False)
