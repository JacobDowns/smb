from dolfin import *
import numpy as np
from scipy import interpolate

"""
Model inputs that are common to both models. This includes initial ice thickness
and length, length dependent bed elevation, and beta2.
"""

class CommonInputsRealistic(object):

    def __init__(self, input_file_name):

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
                self.degree=degree

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
        # Initial length
        self.L0 = Function(self.V_r)


        # Load initial thickness, velocity, and length from a file
        #self.input_file.read(self.H0, "/H0")
        #self.input_file.read(self.H0_c, "/H0_c")
        self.input_file.read(self.L0, "L0")
        self.input_file.read(self.B, "B")
        self.L_init = self.L0.vector().array()[0]

        self.mesh_coords = self.mesh.coordinates()[:,0]
        self.B_interp = interpolate.interp1d(self.mesh_coords, project(self.B).compute_vertex_values())

        print self.B_interp(self.mesh_coords)

        """
        xs = np.linspace(0., 1., 801)
        print xs
        print self.B_interp(xs * 402153.83336364)

        new_mesh = IntervalMesh(800, 0, 1)
        V_new = FunctionSpace(new_mesh, 'CG', 1)
        B_new = Function(V_new)

        print len(B_new.vector())
        print len(xs)
        B_new.vector()[:] = self.B_interp(xs * 402153.83336364)
        plot(B_new, interactive = True)

        self.L0.assign(Constant(self.mesh_coords[-1]))

        out_file = HDF5File(mpi_comm_world(), "is.h5", 'w')
        out_file.write(new_mesh, "mesh")
        out_file.write(B_new, "B")
        out_file.write(self.L0, "L0")
        out_file.close()
        #self.out_file.write(self.H0, "H_init")
        #self.out_file.write(self.get_S(), "S_init")
        #self.out_file.write(self.L0, "L_init")
        #self.out_file.close()
        quit()
        #self.assign_B(400e3)
        #plot(self.B, interactive = True)"""

        #print len(self.mesh_coords)
        #new_mesh = IntervalMesh(193,
        quit()

        # Input expressions
        self.B_exp = B(self.L_init, degree = 1)
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
        # Computes B at vertex coordinates
        self.B.vector()[:] = self.B_interp(self.mesh_coords * L)[::-1]

inputs = CommonInputsRealistic('is.h5')
