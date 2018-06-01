from dolfin import *
import numpy as np
from common_inputs import *
from scipy.interpolate import interp1d
from pdd_calculator import PDDCalculator
import matplotlib.pyplot as plt
from shutil import copyfile

"""
Inputs for steady state paleo run.
"""

class ForwardPaleoInputsSteady1(CommonInputs):

    def __init__(self, input_file_name, dt = 1.):

        ### Load monthly modern temp. and precip. fields
        ########################################################################

        additional_cg_fields = ['T' + str(i) for i in range(12)] \
         + ['P' + str(i) for i in range(12)] + ['S_ref'] + ['adot_prime_func']
        additional_interp_fields = additional_cg_fields

        input_options = {
            'additional_cg_fields' : additional_cg_fields,
            'additional_interp_fields' : additional_interp_fields
        }

        self.additional_cg_fields = additional_cg_fields

        super(ForwardPaleoInputsSteady1, self).__init__(input_file_name, input_options)

        # Initialize the inputs with the correct initial length
        self.update_interp_all(float(self.input_functions['L0']))
        # Surface mass blance function
        self.adot = Function(self.V_cg)
        self.adot.assign(self.original_cg_functions['adot_prime_func'])
        # Initial glacier length
        self.L_init = float(self.input_functions['L0'])
        # Model time step (in years)
        self.dt = dt
        # Object for calculating PDD's
        self.pdd_calc = PDDCalculator(5.5)


        ### Load isotope record used to scale temperature
        ########################################################################

        isotope_data = np.loadtxt('paleo_inputs/d180.csv')
        # Year before present
        years = isotope_data[:,0]
        # Isotope concentration or something
        d180 = isotope_data[:,1]
        # Interpolate the isotope record
        self.dpermil = 2.4
        self.delta_temp_interp = interp1d(years, self.dpermil*(d180 + 34.83), kind = 'linear')


        ### Create monthly reference temperatures for the start year
        ########################################################################

        start_year = -12.5e3
        # Compute reference monthly reference temps. for the start year
        self.delta_temp = float(self.delta_temp_interp(start_year))
        # Elevation lapse rate (degrees C / km)
        self.lapse_rate = 5.
        # Ablation rate for snow (m / (degree C * day))
        self.lambda_snow = 0.005
        # Ablation rate ice (m / (degree C * day))
        self.lambda_ice = 0.008


    """
    Adot expression used by the model.
    """
    def get_adot_exp(self, S):
        # Just return local copy of adot that gets updated as elevation changes
        self.modeled_S = S
        return self.adot


    """
    Recompute SMB as elevation changes.
    """
    def update_adot(self):
        pass #self.adot.vector()[:] = smb


    # Update inputs that change with length, iteration, time, and time step
    def update_inputs(self, L, i = None, t = None, dt = None):
        self.update_interp_all(L)
        self.update_adot()
