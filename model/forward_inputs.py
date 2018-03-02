from dolfin import *
from common_inputs import *

"""
Model inputs for the reverse model. This includes common inputs as well as glacier
length L.
"""

class ForwardInputs1(CommonInputs):

    def __init__(self, input_file_name):

        super(ForwardInputs, self).__init__(input_file_name)
        # SMB
        self.adot = Function(self.V_cg)
        # Number of steps
        self.N = self.input_file.attributes("adot")['count']
        # Time step
        dt = Function(self.V_r)
        self.input_file.read(dt, "dt")
        self.dt = float(dt)


    # Update iteration and length
    def update(self, i, L):
        self.input_file.read(self.adot, "adot/vector_" + str(i))
        self.update_L(self.L)
