from dolfin import *
import numpy as np
from scipy import interpolate

"""
Model inputs that are common to both models. This includes initial ice thickness
and length, length dependent bed elevation, and beta2.
"""

class CommonInputsRealistic(object):

    def __init__(self, input_file_name, L_init = 350e3):

        # Load the mesh for the model
        self.mesh = Mesh()
        self.input_file  = HDF5File(self.mesh.mpi_comm(), input_file_name, "r")
        self.input_file.read(self.mesh, "/mesh", False)

        # Create function space for input data
        self.E_cg = FiniteElement("CG", self.mesh.ufl_cell(), 1)
        self.E_dg = FiniteElement("DG", self.mesh.ufl_cell(), 0)
        self.E_r = FiniteElement("R",  self.mesh.ufl_cell(), 0)
        self.V_cg = FunctionSpace(self.mesh, self.E_cg)
        self.V_dg = FunctionSpace(self.mesh, self.E_dg)
        self.V_r = FunctionSpace(self.mesh, self.E_r)

        # Basal traction
        class Beta2(Expression):
            def __init__(self, L_initial, degree=1):
                self.L = L_initial
                self.degree = degree

            def eval(self,values,x):
                values[0] = 1e-3


        ### Functions for storing inputs
        ########################################################################

        # Initial DG thickness
        self.H0 = Function(self.V_dg)
        # Initial CG thickness
        self.H0_c = Function(self.V_cg)
        # Bed
        self.B = Function(self.V_cg)
        # Basal traction
        self.beta2 = Function(self.V_cg)
        # Initial glacier length
        self.L0 = Function(self.V_r)
        # Domain length (The length of the flowline along which we have data)
        self.domain_length = float(Function(self.V_r))
        # Initial glacier length as float
        self.L_init = L_init

        # Load initial thickness, velocity, and length from a file
        self.input_file.read(self.H0, "/H0")
        self.input_file.read(self.H0_c, "/H0_c")
        self.input_file.read(self.L0, "L0")
        self.input_file.read(self.B, "B")
        self.input_file.read(self.domain_length, "domain_length")
        self.L_init = self.L0.vector().array()[0]
        print self.L_init


        ### Interpolated bed
        ########################################################################
        self.mesh_coords = self.mesh.coordinates()[:,0]
        self.B_interp = interpolate.interp1d(self.mesh_coords, project(self.B).compute_vertex_values())


        ### Create the initial thickness profile
        ########################################################################

        # Bed elevation at desired margin position
        B_margin = self.B_interp(self.L_init / self.domain_length)

        # Surface expression
        class SExp(Expression):
            def eval(self,values,x):
                values[0] = np.sqrt((3500.+ b_frac)**2*(1. - x[0])) + B_margin


        S = project(SExp(degree = 1), self.V_cg)
        # Initialize bed
        self.assign_B(self.L_init)
        # Compute initial thickness
        self.H0_c.assign(project(S - self.B, self.V_cg))
        self.H0_c.vector()[:] += 1.
        # As DG function
        self.H0.assign(self.H0_c)


        print "asdf"
        plot(self.H0, interactive = True)
        quit()


        ### Other input expressions
        ########################################################################
        self.beta2_exp = Beta2(self.L_init, degree = 1)


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


    def assign_B(self, L):
        frac = L / self.domain_length
        # Computes B at vertex coordinates
        self.B.vector()[:] = np.ascontiguousarray(self.B_interp(self.mesh_coords * frac)[::-1])
