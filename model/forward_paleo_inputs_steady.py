from dolfin import *
import numpy as np
from common_inputs import *

"""
Replay forward inputs (replays an inverse model run in the forwrad model.)
"""

class ForwardPaleoInputsSteady(CommonInputs):

    def __init__(self, input_file_name):

        ### Load monthly modern temp. and precip. fields
        ########################################################################

        additional_cg_fields = ['T' + str(i) for i in range(12)] + ['P' + str(i) for i in range(12)]
        additional_interp_fields = additional_cg_fields

        input_options = {
            'additional_cg_fields' : additional_cg_fields,
            'additional_interp_fields' : additional_interp_fields
        }

        super(ForwardPaleoInputsSteady, self).__init__(input_file_name, input_options)

        # Surface mass blance function
        self.adot = Function(self.V_cg)


        ### Load isotope record used to scale temperature
        ########################################################################

        


    # Return the smb expression, just ignore the surface
    def get_adot_exp(self, S):


        # Save the surface elevation function because we'll need this to
        # compute SMB
        self.S = S
        # Just return the local adot function
        return self.adot


    # Update inputs that change with length, iteration, time, and time step
    #def update_inputs(self, i, t, L, dt):





inputs = ForwardPaleoInputsSteady('is_flowline.h5')

print inputs.interp_functions.keys()
