from model.random_inverse_inputs import *
from model.inverse_model.inverse_ice_model import *

import sys
# Integer index
index = int(sys.argv[1])

print "index", index


inverse_inputs = RandomInverseInputs('steady_bumps.hdf5')
model = InverseIceModel(inverse_inputs, 'sample_output/' + str(index), "replay_bumps")
N = 25

for i in range(N):
    inverse_inputs.randomize()
    rates, Ls = np.array(model.run(1., 6000))
    model.reset()
    np.savetxt('sample_rates/' + str(index*N + i) + '.txt', rates)
    np.savetxt('sample_lengths/' + str(index*N + i) + '.txt', Ls)
