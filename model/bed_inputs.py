from dolfin import *
import numpy as np
from scipy.interpolate import UnivariateSpline

"""
Load and interpolate bed data.
"""

class BedInputs(object):

    def __init__(self, inputs, bed_file):

        # Model inputs
        self.inputs = inputs


        ### Mesh and function spaces
        ########################################################################

        self.mesh = Mesh()

        bed_file.read(self.mesh, "/B_mesh", False)
        V_cg = FunctionSpace(self.mesh, 'CG', 1)
        V_r = FunctionSpace(self.mesh, 'R', 0)


        ### Interpolate the bed
        ########################################################################

        # Load the bed data
        B = Function(V_cg)
        bed_file.read(B, "B_data")
        self.B = B

        # Load the domain length
        domain_length_func = Function(V_r)
        bed_file.read(domain_length_func, "domain_length")
        self.domain_length_func = domain_length_func
        self.domain_length = float(domain_length_func)

        # Get the bed mesh coordinates
        mesh_coords = self.mesh.coordinates()[:,0]
        # Normalize so that coordinates go from 0 to 1
        mesh_coords /= mesh_coords.max()
        # Interpolated bed function, needed to determine the inital thickness
        self.B_interp = UnivariateSpline(mesh_coords, project(B).compute_vertex_values(), k = 3, s =  0.1)

        #plot(self.B, interactive = True)
        #self.B.vector()[:] = np.ascontiguousarray(self.B_interp(mesh_coords)[::-1])
        #plot(self.B, interactive = True)


    # Set B in the model inputs object
    def update(self, L):
        frac = L / self.domain_length
        # Computes B at vertex coordinates
        self.inputs.B.vector()[:] = np.ascontiguousarray(self.B_interp(self.inputs.mesh_coords * frac)[::-1])


    # Get bed elevation at a point
    def get_B(self, x):
        frac = x / self.domain_length
        return self.B_interp(frac)
