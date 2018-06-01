import numpy as np
from dolfin import *

class LengthForm(object):
    """
    Set up the variational form for length, or more specically, the H(x=1)=0
    boundary condition.
    """

    def __init__(self, model):

        # CG thickness
        H_c = model.H_c
        # Real test function
        chi = model.chi
        # Boundary measure
        ds1 = dolfin.ds(subdomain_data = model.boundaries)
        # Length residual
        R_length = (H_c - Constant(15.0))*chi*ds1(1)
        self.R_length = R_length
