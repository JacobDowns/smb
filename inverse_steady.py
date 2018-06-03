from model.inputs.inverse_inputs import *
from model.inputs.adot_inputs_elevation_dependent import *
from model.inverse_model.inverse_ice_model import *
from scipy.interpolate import UnivariateSpline
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d


### Linearly interpolate between moraine postions
####################################################################

L_offset =  lambda x : 0.
L_offset_der = lambda x : 0.


### Define model inputs
####################################################################
adot_inputs = AdotInputsElevationDependent()
inputs = InverseInputs('paleo_inputs/is_paleo_11_6_steady.hdf5', L_offset, L_offset_der, adot_inputs)
#inputs = InverseInputs('paleo_inputs/inverse_steady.hdf5', L_offset, L_offset_der, adot_inputs)
model = InverseIceModel(inputs, 'out')

adots = []
for i in range(5000):
    adot0, L = model.step(2.5)


model.write_steady_file('paleo_inputs/inverse_steady')



                               
