from dolfin import *
import numpy as np
from common_inputs import *
from scipy.interpolate import interp1d
from pdd_calculator import PDDCalculator
import matplotlib.pyplot as plt
"""
Inputs for steady transient paleo run.
"""

class ForwardPaleoInputs(CommonInputs):

    def __init__(self, input_file_name, dt = 1., delta_temp_record = 'buizert'):

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
        super(ForwardPaleoInputs, self).__init__(input_file_name, input_options)

        # Initialize the inputs with the correct initial length
        self.update_interp_all(float(self.input_functions['L0']))
        # Surface mass blance function
        self.adot = Function(self.V_cg)
        # Precipitation for the given year (for plotting) in m/a
        self.precip = Function(self.V_cg)
        # Temperature for the given year (for plotting) in C
        self.temp = Function(self.V_cg)
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
        self.delta_temp_interp = interp1d(years, self.dpermil*(d180 + 34.83), kind = 'linear')"""


        ### Load inverted surface temps from DYE3 ice core
        ########################################################################

        if delta_temp_record == 'jensen':
            data = np.loadtxt('jensen_dye3.txt')
            # Years before present (2000)
            years = data[:,0] - 2000.0
            # Temps. in K
            temps = data[:,1]
        elif delta_temp_record == 'buizert':
            data = np.loadtxt('buizert_dye3.txt')
            years = -data[:,0][::-1]
            temps = data[:,1][::-1]
        elif delta_temp_record == 'ngrip':
            data = np.loadtxt('paleo_inputs/d180.csv')
            years = data[:,0]
            # Isotope concentration
            d180 = data[:,1]
            # Conversion to delta temp
            self.dpermil = 2.4
            temps = self.dpermil*(d180 + 34.83)

        # Interpolated delta temp. field
        self.delta_temp_interp = interp1d(years, temps - temps[-1], kind = 'linear')

        
        #years = np.linspace(-12.5e3, -20., 500)
        #plt.plot(years, self.delta_temp_interp(years))
        #plt.show()
    
        
        ### Create monthly reference temperatures for the start year
        ########################################################################

        self.start_year = -11.6e3 #-12.5e3
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
    Recompute SMB as time and ice surface change.
    """
    def update_adot(self, year):

        ### Compute monthly pdd's and precip.
        ########################################################################

        # Compute temperature offset from modern
        delta_temp = float(self.delta_temp_interp(year))

        print year, delta_temp

        # Accumulated snowpack for the year accumulation - ablation
        snowpack = np.zeros_like(self.input_functions['S_ref'].vector().get_local())
        # Yearly ice ablation
        ablation = np.zeros_like(self.input_functions['S_ref'].vector().get_local())
        # Get the reference elevation used by climate model
        ref_elevation_vec = self.input_functions['S_ref'].vector().get_local()
        # Get the modeled elevation
        modeled_elevation_vec = self.modeled_S.vector().get_local()
        # Compute the lapse rate correction in C
        lapse_correction = ((ref_elevation_vec - modeled_elevation_vec) / 1000.0) * self.lapse_rate

        for i in range(12):
            # Compute the delta temp. adjusted / lapse rate corrected temp. for this month
            modern_temp_vec = self.input_functions['T' + str(i)].vector().get_local()
            temp_vec = modern_temp_vec + delta_temp + lapse_correction
            # Compute the delta temp. adjusted precip.
            modern_precip_vec = self.input_functions['P' + str(i)].vector().get_local()
            # Temp. corrected precip. rate in m.w.e./a
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
                # Ablation m.w.e
                ablation += ice_pdds * self.lambda_ice

            # Update snowpack
            snowpack -= monthly_snowmelt
            snowpack[snowpack < 0.] = 0.

        # Total mass balance in m.i.e. assuming snowpack turns to ice at end of year
        smb = (snowpack - ablation) * (10./9.)
        self.adot.vector()[:] = smb


    # Update inputs that change with length, iteration, time, and time step
    def update_inputs(self, L, i = None, t = None, dt = None):
        year = self.start_year + t
        self.update_interp_all(L)
        self.update_adot(year)
