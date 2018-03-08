from dolfin import *
import numpy as np
#from scipy import interpolate
from scipy.interpolate import UnivariateSpline

class ForwardInputsRealisticSteady(object):

    def __init__(self, input_file_name, L_init = 390e3, L_steady = 400e3, adot_max = 0.5, dt = 1., N = 75000):

        # Time step
        self.dt = dt
        # Number of steps to take
        self.N = N


        ### Stuff for loading bed data
        ########################################################################

        # Load data mesh
        data_mesh = Mesh()
        input_file  = HDF5File(data_mesh.mpi_comm(), input_file_name, "r")
        input_file.read(data_mesh, "/mesh", False)
        # Function space for loading data
        V_cg_data = FunctionSpace(data_mesh, 'CG', 1)
        V_r_data = FunctionSpace(data_mesh, 'R', 0)

        # Function for loading bed data
        B_data = Function(V_cg_data)
        # Domain length (The length of the flowline along which we have data)
        domain_length_func = Function(V_r_data)


        ### Interpolated bed
        ########################################################################

        input_file.read(B_data, "B")
        input_file.read(domain_length_func, "domain_length")
        self.domain_length = float(domain_length_func)

        #self.B_interp = interpolate.interp1d(data_mesh.coordinates()[:,0], project(B_data).compute_vertex_values())
        self.B_interp =  UnivariateSpline(data_mesh.coordinates()[:,0][::5], project(B_data).compute_vertex_values()[::5], k = 3, s =  1)

        ### Model mesh and function spaces
        ########################################################################

        # Create a model mesh
        self.mesh = IntervalMesh(800, 0., 1.)
        # Model mesh coordinates
        self.mesh_coords = self.mesh.coordinates()[:,0]

        # Create function space for input data
        self.E_cg = FiniteElement("CG", self.mesh.ufl_cell(), 1)
        self.E_dg = FiniteElement("DG", self.mesh.ufl_cell(), 0)
        self.E_r = FiniteElement("R",  self.mesh.ufl_cell(), 0)
        self.V_cg = FunctionSpace(self.mesh, self.E_cg)
        self.V_dg = FunctionSpace(self.mesh, self.E_dg)
        self.V_r = FunctionSpace(self.mesh, self.E_r)


        ### Input expressions
        ########################################################################

        # Basal traction
        class Beta2(Expression):
            def __init__(self, L_initial, degree=1):
                self.L = L_initial
                self.degree = degree

            def eval(self,values,x):
                values[0] = 1e-3


        # Surface mass balance
        class Adot(Expression):
            def __init__(self, L_initial, degree=1):
                self.L = L_initial
                self.degree = degree

            def eval(self, values, x):
                x = x[0]*self.L
                values[0] = adot_max*(1.0 - 2.0*(x / L_steady))


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
        self.L_init = L_init


        ### Create the initial thickness profile
        ########################################################################

        # Bed elevation at desired margin position
        B_margin = self.B_interp(self.L_init / float(self.domain_length))

        # Surface expression
        class SExp(Expression):
            def eval(self,values,x):
                values[0] = np.sqrt((3200.+ B_margin)**2*(1. - x[0])) + B_margin
                #values[0] = 2000.*(1. - x[0]**2) + 1.

        S = project(SExp(degree = 1), self.V_cg)
        # Initialize bed
        self.assign_B(self.L_init)
        # Compute initial thickness
        self.H0_c.assign(project(S - self.B, self.V_cg))
        # As DG function
        self.H0.assign(project(self.H0_c, self.V_dg))


        ### Other input expressions
        ########################################################################
        self.beta2_exp = Beta2(self.L_init, degree = 1)
        self.adot_exp = Adot(self.L_init, degree = 1)


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


    # Update B given length
    def assign_B(self, L):
        frac = L / self.domain_length
        # Computes B at vertex coordinates
        self.B.vector()[:] = np.ascontiguousarray(self.B_interp(self.mesh_coords * frac)[::-1])


    # Update iteration and length
    def assign_inputs(self, i, L):
        self.adot_exp.L = L
        self.beta2_exp.L = L
        self.beta2.interpolate(self.beta2_exp)
        self.assign_B(L)


    # Surface mass balance expression
    def adot_expression(self, S):
        return self.adot_exp
