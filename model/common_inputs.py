from dolfin import *
import numpy as np
from bed_inputs import *

"""
Flexible class for generating a forward model inputs file.
"""

class CommonInputs(object):

    def __init__(self, input_file_name, adot_inputs):

        ### Mesh and function spaces
        ########################################################################

        self.mesh = Mesh()
        input_file = HDF5File(self.mesh.mpi_comm(), input_file_name, "r")
        self.input_file = input_file
        input_file.read(self.mesh, "/mesh", False)
        self.mesh_coords = self.mesh.coordinates()[:,0]

        self.E_cg = FiniteElement('CG', self.mesh.ufl_cell(), 1)
        self.E_dg = FiniteElement('DG', self.mesh.ufl_cell(), 0)
        self.E_r = FiniteElement('R',  self.mesh.ufl_cell(), 0)
        self.V_cg = FunctionSpace(self.mesh, self.E_cg)
        self.V_dg = FunctionSpace(self.mesh, self.E_dg)
        self.V_r = FunctionSpace(self.mesh, self.E_r)


        ### Initialize inputs
        ########################################################################

        # Bed function
        self.B = Function(self.V_cg)
        # Width
        self.width = Function(self.V_cg)
        # Spatial derivative of width
        self.width_dx = Function(self.V_cg)
        # Load bed data from the input file
        self.bed_inputs = BedInputs(self, input_file)
        # Store the bed mesh and data
        self.B_mesh = self.bed_inputs.mesh
        self.B_data = self.bed_inputs.B
        self.domain_length = self.bed_inputs.domain_length_func

        # DG thickness
        self.H0 = Function(self.V_dg)
        input_file.read(self.H0, "H0")

        # CG thickness
        self.H0_c = Function(self.V_cg)
        input_file.read(self.H0_c, "H0_c")

        # Basal traction
        self.beta2 = Function(self.V_cg)
        self.beta2.assign(Constant(1e-3))

        # Initial glacier length
        self.L0 = Function(self.V_r)
        input_file.read(self.L0, "L0")
        self.L_init = float(self.L0)

        # Object that encapsulates an smb expression
        self.adot_inputs = adot_inputs


        #### Create boundary facet function
        ########################################################################
        self.boundaries = FacetFunctionSizet(self.mesh, 0)

        for f in facets(self.mesh):
            if near(f.midpoint().x(), 1):
                # Terminus
               self.boundaries[f] = 1
            if near(f.midpoint().x(), 0):
               # Divide
               self.boundaries[f] = 2


    # Update inputs that change with length, iteration, time, and time step
    def update_inputs(self, i, t, L, dt):
        # Assign bed function
        self.bed_inputs.update(L)
        # Update adto expression
        self.adot_inputs.update(t, L)


    # Return the smb expression, just ignore the surface
    def get_adot_exp(self, S, adot_param = None):
        return self.adot_inputs.get_adot_exp(S, adot_param)
