from dolfin import *
import numpy as np
from bed_inputs import *

"""
Flexible class for generating a forward model inputs file.
"""

class GenInputs(object):

    def __init__(self, inputs_dict):

        ### Mesh and function spaces
        ########################################################################

        N = 1200
        if 'cell_count' in inputs_dict:
            N = inputs_dict['cell_count']

        mesh = IntervalMesh(N, 0., 1.)
        self.mesh_coords = mesh.coordinates()[:,0]

        V_cg = FunctionSpace(mesh, 'CG', 1)
        V_dg = FunctionSpace(mesh, 'DG', 0)
        V_r = FunctionSpace(mesh, 'R', 0)


        ### Bed data
        ########################################################################

        # Bed function
        self.B = Function(V_cg)
        # Width
        self.width = Function(V_cg)
        # Open file with bed data
        bed_file = HDF5File(mesh.mpi_comm(), inputs_dict['bed_file_name'], "r")
        # Load bed data from file
        bed_inputs = BedInputs(self, bed_file)
        # Assign bed function
        bed_inputs.update(inputs_dict['L_init'])


        #### Initial thickness
        ########################################################################

        # Continuous thickness
        H0 = Function(V_cg)
        # DG thickness
        H0_c = Function(V_dg)
        # Get the bed elevation at the desired terminus position
        B_term = bed_inputs.get_B(inputs_dict['L_init'])

        H_max = 3000.
        if 'H_max' in inputs_dict:
            H_max = inputs_dict['H_max']

        # Surface expression
        class SExp(Expression):
            def eval(self,values,x):
                values[0] = np.sqrt((H_max + B_term)**2*(1. - x[0])) + B_term

        S = project(SExp(degree = 1), V_cg)
        # Compute initial thickness
        H0_c.assign(project(S - self.B, V_cg))
        # As DG function
        H0.assign(project(H0_c, V_dg))

        # Initial glacier length
        L0 = Function(V_r)
        L0.assign(Constant(inputs_dict['L_init']))


        ### Write a model inputs file
        ########################################################################

        out_file = HDF5File(mesh.mpi_comm(), inputs_dict['out_file'] + '.h5', "w")

        # Write the bed data
        out_file.write(bed_inputs.mesh, "B_mesh")
        out_file.write(bed_inputs.B, "B_data")
        out_file.write(bed_inputs.width, "width_data")
        out_file.write(bed_inputs.domain_length_func, "domain_length")

        # Write the model data
        out_file.write(mesh, "mesh")
        out_file.write(H0, "H0")
        out_file.write(H0_c, "H0_c")
        out_file.write(L0, "L0")
        out_file.close()


inputs_dict = {}
inputs_dict['cell_count'] = 1200
inputs_dict['input_file'] = '../forward_inputs/is_mesh_new.h5'
inputs_dict['L_init'] = 390e3
inputs_dict['H_max'] = 2450.
inputs_dict['out_file'] = '../forward_inputs/is_inputs_width'

gi = GenInputs(inputs_dict)
