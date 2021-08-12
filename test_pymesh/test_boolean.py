import pymesh
import numpy as np
from pymesh.meshio import load_mesh


def load_cube():
    cube_filename = "/Users/jared/PyMesh/tests/data/cube.obj"   #cube goes from -1 to 1
    cube_mesh = pymesh.load_mesh(cube_filename)
    return cube_mesh

def load_ball():
    ball_filename = "/Users/jared/PyMesh/tests/data/ball.msh"   #ball has radius 1
    ball_mesh = pymesh.load_mesh(ball_filename)
    return ball_mesh

def scaled_mesh(input_mesh, scale):
    scaled_vertices = input_mesh.vertices * scale
    new_mesh = pymesh.form_mesh(scaled_vertices, input_mesh.faces)
    return new_mesh



def main():
    ###### loading ball and cube from mesh files that already exist  #########
    # ball_mesh = load_ball()
    # cube_mesh = load_cube()

    # # scale ball so that overlap of 2 shapes is not just the ball shape
    # ball_mesh = scaled_mesh(ball_mesh, 1.25)

    ####### generating ball and cube from built-in functions ##########
    ball_mesh = pymesh.generate_icosphere(radius=1.2, center=[0,0,0], refinement_order=3)
    cube_mesh = pymesh.generate_box_mesh(box_min=[-1,-1,-1], box_max=[1,1,1])

    # perform boolean
    output_mesh = pymesh.boolean(cube_mesh, ball_mesh, operation="difference")

    # write mesh to file
    output_file = "test_boolean_mesh.obj"
    pymesh.save_mesh(output_file, output_mesh)



if __name__ == "__main__":
    main()