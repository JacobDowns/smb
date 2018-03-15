from model.inverse_inputs import *
from model.length_inputs_interp import *
from model.adot_inputs_elevation_dependent import *
from model.inverse_model.inverse_ice_model import *
import matplotlib.pyplot as plt
from scipy.optimize import minimize


### Variables to parameterize the length curve
################################################################################

# Times
ts = np.array([0.0, 250., 500.])
# Offsets
offsets = -ts * (150e3 / 6000)
# Array of control variables (controls the offset position between every two observations
x0 =  offsets[1::2]


### Setup the inverse model
################################################################################

adot_inputs = AdotInputsElevationDependent()
length_inputs = LengthInputsInterp(ts, offsets)

inputs = InverseInputs('is_steady_elevation_dependent.hdf5', adot_inputs, length_inputs, dt = 1., N = 100)
model = InverseIceModel(inputs, "out", "is_thing")



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
    length_inputs.set(ts, offsets)

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
    #plt.plot(adot_params)
    #plt.show()

    #return ((adot_params[1:] - adot_params[:1])**2).sum()
    return adot_params

p1 = F(x0)
p2 = F(x0)

print p1
print p2

"""
l_bound = list(x0 - 2000.)
u_bound = list(x0 + 2000.)
bounds = tuple(zip(l_bound, u_bound))

res = minimize(F, x0, method='SLSQP', bounds=bounds, tol = 1e-3)"""
