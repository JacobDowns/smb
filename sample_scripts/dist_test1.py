from model.random_inverse_inputs import *
from model.inverse_model.inverse_ice_model import *

inverse_inputs = RandomInverseInputs('steady_bumps.hdf5')
model = InverseIceModel(inverse_inputs, "out", "replay_bumps")

ts = np.linspace(0.0, 6000.0, 6000)

import matplotlib.pyplot as plt

for i in range(5):
    adots = np.array(model.run(1., 6000))
    model.reset()

    plt.plot(ts, adots)

    print adots

plt.show()
