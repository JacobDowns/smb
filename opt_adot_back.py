from model.inverse_inputs import *
from model.length_inputs_interp import *
from model.adot_inputs_elevation_dependent import *
from model.inverse_model.inverse_ice_model import *
import matplotlib.pyplot as plt
from scipy.optimize import minimize
from scipy.signal import savgol_filter


### Variables to parameterize the length curve
################################################################################

# Times
ts = np.array([0.0, 500., 1000., 1500., 2000., 2500., 3000., 3500., 4000., 4500., 5000., 5500., 6000.])
# Offsets
offsets = -ts * (150e3 / 6000)
# Array of control variables (controls the offset position between every two observations
x0 =  offsets[1::2]


### Setup the inverse model
################################################################################

adot_inputs = AdotInputsElevationDependent()
length_inputs = LengthInputsInterp(ts, offsets)

inputs = InverseInputs('is_steady_elevation_dependent.hdf5', adot_inputs, length_inputs, dt = 1., N = 3000)
model = InverseIceModel(inputs, "out", "is_replay_steady_elevation_dependent")


### Objective function
################################################################################

"""
Objective function that measures the smoothness of the climate forcing. The control
variables parameterize how length changes through time, specifically in between
observation points.
"""

def F(x):
    print "x", x
    print

    # Set offsets
    offsets[1::2] = x[:]
    #length_inputs.set(ts, offsets)


    ts1 = np.linspace(0., 6000., 250)
    things = map(length_inputs.get_L_offset, ts1)

    plt.plot(ts1, things)
    plt.plot(ts, offsets, 'ko')
    plt.show()

    # Reset the model (start back from time 0)
    model.reset()
    # Stores value of smb param through time
    adot_params = []

    while model.i < model.steps:
        adot0 = model.step()
        adot_params.append(adot0)

    adot_params = np.array(adot_params)
    plt.plot(adot_params)
    plt.plot(savgol_filter(adot_params, 601, 3))
    plt.show()

    return ((adot_params[1:] - adot_params[:1])**2).sum()

"""
l_bound = list(x0 - 8000.)
u_bound = list(x0 + 8000.)
bounds = zip(l_bound, u_bound)

res = minimize(F, x0, method='SLSQP', bounds=bounds, tol = 1e-3)"""


F(x0)
