from dolfin import *
import numpy as np

"""
Flexible model inputs object that compiles inputs.
"""

class Inputs(object):

    def __init__(self, inputs_dict):

        ### Mesh and function spaces
        ########################################################################

        N = inputs_dict['cell_count']
        self.mesh = IntervalMesh(N, 0., 1.)


        #### Bed

        bed_type = 'synthetic'

        if 'bed' in inputs_dict:
            bed_type = inputs_dict['bed_type']


        if bed_type == 'realistic':



        ### Data mesh and function spaces
        ########################################################################

        # Load the mesh for the model
        self.data_mesh = Mesh()
        self.input_file  = HDF5File(self.mesh.mpi_comm(), input_file_name, "r")
        self.input_file.read(self.data_mesh, "/mesh", False)
        self.V_cg_data = FunctionSpace(self.data_mesh, 'CG', 1)
        self.V_r_data = FunctionSpace(self.data_mesh, 'R', 0)


        ### Create an interpolated bed function
        ########################################################################

        # Function for loading bed data
        B_data = Function(self.V_cg_data)
        input_file.read(self.V_r_data, "B")
        # Domain length (The length of the flowline along which we have data)
        domain_length_func = Function(self.V_r_data )
        input_file.read(domain_length_func, "domain_length")
        # Domain length as float
        self.domain_length = float(domain_length_func)
        # Interpolated bed function
        self.B_interp =  UnivariateSpline(data_mesh.coordinates()[:,0][::5], project(B_data).compute_vertex_values()[::5], k = 3, s =  1)


    # Assign
    def assign_B(self):
        frac = L / self.domain_length
        # Computes B at vertex coordinates
        self.inputs.B.vector()[:] = np.ascontiguousarray(self.B_interp(self.inputs.mesh_coords * frac)[::-1])
