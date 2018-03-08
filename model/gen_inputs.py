from dolfin import *
import numpy as np

"""
Flexible class for generating a forward model inputs file.
"""

class GenInputs(object):

    def __init__(self, inputs_dict):

        ### Mesh and function spaces
        ########################################################################

        N = inputs_dict['cell_count']
        mesh = IntervalMesh(N, 0., 1.)

        V_cg = FunctionSpace(mesh, 'CG', 1)
        V_cg = FunctionSpace(mesh, 'CG', 1)
        V_r = FunctionSpace(mesh, 'R', 0)


        ### Bed data
        ########################################################################

        bed_mesh = Mesh()
        bed_file = HDF5File(bed_mesh.mpi_comm(), inputs_dict['bed_file'], "r")
        bed_file.read(bed_mesh, "/mesh", False)
        V_cg_bed = FunctionSpace(data_mesh, 'CG', 1)
        V_r_bed = FunctionSpace(data_mesh, 'R', 0)

        # Load the bed data
        B = Function(V_cg_bed)
        bed_file.read(B, "B")
        # Load the domain length
        domain_length_func = Function(V_r_bed)
        input_file.read(domain_length_func, "domain_length")


        ### Interpolate the bed
        ########################################################################

        # Get the bed mesh coordinates
        bed_mesh_coords = bed_mesh.coordinates()[:,0]
        # Normalize so that coordinates go from 0 to 1
        bed_mesh_coords /= bed_mesh_coords.max()
        # Interpolated bed function, needed (kind of) to determine the inital thickness
        B_interp =  UnivariateSpline(bed_mesh_coords, project(B).compute_vertex_values(), k = 3, s =  1)


        #### Initial thickness
        ########################################################################

        # Get the desired initial glacier length
        L_init = inputs_dict['L_init']
        # Get the bed elevation at the desired terminus position
        frac = L_init / float(domain_length_func)
        B_term = B_interp(frac)

        quit()
