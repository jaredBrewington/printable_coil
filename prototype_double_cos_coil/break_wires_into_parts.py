import numpy as np
from glob import glob 
from pprint import pprint
import os


def get_radius(y, z):
    return np.sqrt(y*y+z*z)

def get_coil_dimensions(folder_path):
    """Returns coil dimensions estimated from the points in the middle wire file of folder
        this only works for coils along x axis
    """
    sort_by_wire_num = lambda f: int((os.path.basename(f)).split("wire")[1].split(".")[0])

    files = sorted(glob(folder_path+"/*.txt"), key=sort_by_wire_num)
    half_index = int(len(files)*.5)
    x,y,z = np.loadtxt(files[half_index], unpack=True)
    x_max = np.max(x)
    x_min = np.min(x)
    radius_arr = np.array([np.sqrt(z1*z1 + y1*y1) for z1,y1 in zip(z,y)])
    avg_radius = np.mean(radius_arr)
    return x_max, x_min, avg_radius

def separate_coil_parts(x_max, x_min, radius):
    
    folder = os.path.abspath("mirror_coil1")
    wire_folder = os.path.join(folder, "wires")
    file_list = glob(os.path.join(wire_folder, "*.txt"))
    sep_folder = os.path.join(folder, "sep_wires")
    print(folder)

    for f in file_list:
        wire_name = os.path.basename(f).split(".")[0]
        sep_file_names = [os.path.join(sep_folder, wire_name + "_" + str(i) + ".txt") for i in range(4)]
        x,y,z = np.loadtxt(f, unpack=True)
        if x[0]==x[-1] and y[0]==y[-1] and z[0]==z[-1]:
            x = np.delete(x, -1)
            y = np.delete(y, -1)
            z = np.delete(z, -1)
        f0 = open(sep_file_names[0], "w")
        f1 = open(sep_file_names[1], "w")
        f2 = open(sep_file_names[2], "w")
        f3 = open(sep_file_names[3], "w")
        for X,Y,Z in zip(x,y,z):
            if X == x_max:
                f0.write(f"{X} {Y} {Z}\n")
            elif X == x_min:
                f2.write(f"{X} {Y} {Z}\n")
            elif get_radius(Y,Z) > radius and np.sign(Y)==np.sign(np.max(y)):
                f1.write(f"{X} {Y} {Z}\n")
            else:
                f3.write(f"{X} {Y} {Z}\n")



if __name__ == "__main__":
    folder_name = os.path.abspath("mirror_coil1/wires")
    x_max, x_min, radius = get_coil_dimensions(folder_name)
    separate_coil_parts(x_max, x_min, radius)
