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

class ForwardPaleoInputsSteady(CommonInputs):

    def __init__(self, input_file_name, dt = 1.):

        ### Load monthly modern temp. and precip. fields
        ########################################################################

        additional_cg_fields = ['T' + str(i) for i in range(12)] \
         + ['P' + str(i) for i in range(12)] + ['S_ref']
        additional_interp_fields = additional_cg_fields

        input_options = {
            'additional_cg_fields' : additional_cg_fields,
            'additional_interp_fields' : additional_interp_fields
        }

        self.additional_cg_fields = additional_cg_fields

        super(ForwardPaleoInputsSteady, self).__init__(input_file_name, input_options)

        # Initialize the inputs with the correct initial length
        self.update_interp_all(float(self.input_functions['L0']))
        # Surface mass blance function
        self.adot = Function(self.V_cg)
        # Initial glacier length
        self.L_init = float(self.input_functions['L0'])
        # Model time step (in years)
        self.dt = dt
        # Object for calculating PDD's
        self.pdd_calc = PDDCalculator(5.5)

        
        ### Load isotope record used to scale temperature
        ########################################################################
        """
        isotope_data = np.loadtxt('paleo_inputs/d180.csv')
        # Year before present
        years = isotope_data[:,0]
        # Isotope concentration or something
        d180 = isotope_data[:,1]
        # Interpolate the isotope record
        self.dpermil = 2.4
        self.delta_temp_interp1 = interp1d(years, self.dpermil*(d180 + 34.83), kind = 'linear')"""
        

        ### Load inverted surface temps from DYE3 ice core
        ########################################################################
        
        smooth_temps = np.loadtxt('smooth_dye_temp.txt')
        # Years before present (2000)
        years = smooth_temps[:,0] - 2000.0
        # Temps. in K
        temps = smooth_temps[:,1]
        # Interpolated delta temp. field
        self.delta_temp_interp = interp1d(years, temps - temps[-1], kind = 'linear')
        

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
        # Overide the actual delta temp to get an initial ice sheet that actually makes sense
        self.delta_temp = -8.187

        
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

        ### Compute monthly pdd's and precip.
        ########################################################################

        # Accumulated snowpack for the year accumulation - ablation
        snowpack = np.zeros_like(self.input_functions['S_ref'].vector().get_local())
        # Yearly ice ablation
        ablation = np.zeros_like(self.input_functions['S_ref'].vector().get_local())
        # Get the reference elevation used by climate model
        ref_elevation_vec = self.input_functions['S_ref'].vector().get_local()
        # Get the modeled elevation
        modeled_elevation_vec = self.modeled_S.vector().get_local()
        # Compute the lapse rate correction
        lapse_correction = ((ref_elevation_vec - modeled_elevation_vec) / 1000.0) * self.lapse_rate

        for i in range(12):
            # Compute the delta temp. adjusted / lapse rate corrected temp. for this month
            modern_temp_vec = self.input_functions['T' + str(i)].vector().get_local()
            temp_vec = modern_temp_vec + self.delta_temp + lapse_correction
            # Compute the delta temp. adjusted precip.
            modern_precip_vec = self.input_functions['P' + str(i)].vector().get_local()
            # precip. rate in m.w.e./a
            precip_vec = modern_precip_vec*np.e**(0.07*(temp_vec - modern_temp_vec))
            # Compute pdd's for this month
            pdds = self.pdd_calc.get_pdd(temp_vec)
            # Compute snowfall for this month
            snowfall_frac = self.pdd_calc.get_acc_frac(temp_vec)
            # Compute snowfall for the month in m.w.e
            monthly_snowfall = precip_vec * (1./12.) * snowfall_frac
            snowpack += monthly_snowfall
            # Compute monthly snow melt in m.w.e
            monthly_snowmelt = pdds * self.lambda_snow

            # If the snowpack is depleted, start melting ice
            if (snowpack - monthly_snowmelt).min() < 0.:
                # Number of pdd's required to melt the snow
                snow_pdds = snowpack / self.lambda_snow
                # PDD's that go to melting ice
                ice_pdds = pdds - snow_pdds
                ice_pdds[ice_pdds < 0.] = 0.
                # Add to ice ablation in m.w.e
                ablation += ice_pdds*self.lambda_ice

            # Update snowpack
            snowpack -= monthly_snowmelt
            snowpack[snowpack < 0.] = 0.

        # Total mass balance in m.i.e. assuming snowpack turns to ice at end of year
        smb = (snowpack - ablation) * (10./9.)
        self.adot.vector()[:] = smb


    # Update inputs that change with length, iteration, time, and time step
    def update_inputs(self, L, i = None, t = None, dt = None):
        self.update_interp_all(L)
        self.update_adot()