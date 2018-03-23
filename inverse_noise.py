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

# Number of "true" observation points
num_obs_points = 5
# Number of intermediate points between every two observations
num_int_points = 5
# Times
ts = np.linspace(0., 6000., num_obs_points + (num_obs_points - 1) * num_int_points)
# Has a 1 at sample points and a 0 at observations points
sample_indexes = np.ones(len(ts))
sample_indexes[::(num_int_points+1)] = 0.
# Expected margin offsets through time given linear retreat rate
offsets = -ts * (150e3 / 6000.)
# The length inputs object takes in points, and smoothly interpolates between them
length_inputs = LengthInputsInterp(ts, offsets)


### Setup the model
adot_inputs = AdotInputsElevationDependent()
inputs = InverseInputs('is_steady_elevation_dependent_width.hdf5', adot_inputs, length_inputs, dt = 1., N = 6000)
model = InverseIceModel(inputs, 'sample_output/' + str(index), 'replay_is_rand_' + str(index))


### Create the inverse covariance matrix Q
################################################################################
Q = np.diag(2.*np.ones(num_int_points), 0) + np.diag(-np.ones(num_int_points - 1), -1) + np.diag(-np.ones(num_int_points - 1), 1)
delta = 0.005
h = ts[1]
Q = delta * (1. / h**2) * Q


### Run the model several time, adding random noise to the length
################################################################################

for i in range(N):
    try :
        ### Add noise to the length offset
        noise = np.random.multivariate_normal(np.zeros(num_int_points), np.linalg.inv(Q), num_obs_points - 1).flatten()
        random_offsets = np.zeros(len(offsets))
        random_offsets[:] = offsets
        random_offsets[sample_indexes == 1.] += noise
        length_inputs.set(ts, random_offsets)

        ts1 = np.linspace(0., 6000., 500)
        plt.plot(ts1, np.array(map(length_inputs.get_L_offset, ts1)))
        #plt.show()

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

        np.savetxt('sample_rates/' + str(index*N + i) + '.txt', adot_params)
        np.savetxt('sample_lengths/' + str(index*N + i) + '.txt', lengths)

    except:
        print "Failed"

plt.show()
