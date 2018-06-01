import numpy as np
from dolfin import *

class MassFormFixedDomain(object):
    """
    Set up the variational form for the fixed domain mass balance equation.
    """

    def __init__(self, model):

        # DG thickness
        H = model.H_f
        # Rate of change of H
        dHdt = model.dHdt_f
        # Ice sheet length
        L = model.L_f
        # Velocity
        ubar = model.ubar_f
        # DG test function
        xsi = model.xsi_f
        # Boundary measure
        ds1 = dolfin.ds(subdomain_data = model.boundaries)
        # SMB expression
        adot_prime = model.adot_prime
        # Ice stream width
        width = model.width
        width = Constant(5e3)
        # Flux velocity
        q_vel = ubar
        # Flux
        q_flux = q_vel*H*width
        # Inter element flux (upwind)
        uH = avg(q_vel)*avg(H*width) + 0.5*abs(avg(width*q_vel))*jump(H)


        ### Mass balance residual
        ########################################################################
        R_mass = (L*width*dHdt*xsi - L*width*adot_prime*xsi)*dx
        R_mass += uH*jump(xsi)*dS
        R_mass += q_flux*xsi*ds1(1)

        self.form = q_flux*xsi*ds1(1)
        self.L = L

        self.R_mass = R_mass


    def print_form(self):
        print float(self.L)
