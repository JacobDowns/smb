from model.inverse_inputs import *
from model.length_inputs_interp import *
from model.adot_inputs_elevation_dependent import *
from model.inverse_model.inverse_ice_model import *
import matplotlib.pyplot as plt
import sys
import numpy as np

"""
Introduce noise to the length inputs by drawing from a GMRF.
"""


# Integer index
index = int(sys.argv[1])
print "index", index
#index = 0
N = 25

### Noise parameters
################################################################################

# Generate an array of random offsets
def get_offsets():

    ### Add random noise to the observation points
    ############################################################################

    # Mean observation times
    obs_ts = np.array([0., 1000., 2000., 3000., 4000., 5000., 7000.])
    # Observed offsets
    obs_offsets = -obs_ts * (150e3 / 6000.)
    # Add random noise to observation points
    sigma = 100.
    obs_ts[1:] += 100.*np.random.randn(6)
    # Number of subsample points
    n_sub = 9
    t = np.arange(0, n_sub * len(obs_ts), n_sub)
    tt = np.arange((len(obs_ts) - 1) * n_sub + 1)
    # Array of times including observations times and subsample times
    ts = np.interp(tt, t, obs_ts)
    # Offsets at observations times and subsample times
    Ls = np.interp(ts, obs_ts, obs_offsets)


    ### Add noise between observation points
    ################################################################################

    Q = np.diag(2.*np.ones(n_sub - 1), 0) + np.diag(-np.ones(n_sub - 2), -1) + np.diag(-np.ones(n_sub - 2), 1)
    delta = 0.0000000005
    h = ts[1]
    Q = delta * Q

    sample_indexes = np.ones(len(ts))
    sample_indexes[::n_sub] = 0.

    # Distances between subsample points
    hs = (ts[1:] - ts[:-1])
    hs = hs[np.mod(np.arange(hs.size),n_sub)!=0]

    noise =  (1. / hs) * np.random.multivariate_normal(np.zeros(n_sub - 1), np.linalg.inv(Q), 6).flatten()
    Ls[sample_indexes == 1.] += noise

    return ts, Ls


# The length inputs object takes in points, and smoothly interpolates between them
ts, offsets = get_offsets()
length_inputs = LengthInputsInterp(ts, offsets)
# Setup the model
adot_inputs = AdotInputsElevationDependent()
inputs = InverseInputs('is_steady_elevation_dependent_width.hdf5', adot_inputs, length_inputs, dt = 1., N = 6000)
model = InverseIceModel(inputs, 'sample_output/' + str(index), 'replay_is_rand_' + str(index))


for i in range(N):
    try :
        ### Add random noise to the observation points
        ########################################################################

        ts, offsets = get_offsets()
        length_inputs.set(ts, offsets)

        # Reset the model (start back from time 0)
        model.reset()
        # Stores value of smb param through time
        adot_params = []
        # Lengths
        lengths = []

        while model.i < model.steps:
            adot0, L = model.step()
            #plot(model.width, interactive = False)
            #plot(model.adot_prime_func, interactive = False)
            #plot(model.B, interactive = False)
            adot_params.append(adot0)
            lengths.append(L)

        adot_params = np.array(adot_params)
        lengths = np.array(lengths)

        np.savetxt('sample_rates1/' + str(index*N + i) + '.txt', adot_params)
        np.savetxt('sample_lengths1/' + str(index*N + i) + '.txt', lengths)

    except:
        print "Failed"
