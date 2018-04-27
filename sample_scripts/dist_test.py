"""
from model.inverse_inputs1 import *
from model.inverse_model.inverse_ice_model import *

inverse_inputs = InverseInputs1('steady_bumps.hdf5')
model = InverseIceModel(inverse_inputs, "out", "replay_bumps")
model.run(1., 6000)"""


#import matplotlib.pyplot as plt

import numpy as np
from scipy.interpolate import UnivariateSpline

# Times
ts = np.array([0.0, 1200.0, 2000.0, 3000.0, 4000.0, 5000.0, 6000.0])
#Ls = 500e3 - (ts / 1000.0) * 25000.0
Ls = np.array([500e3, 480e3, 455e3, 425e3, 390e3, 360e3, 340e3])


import matplotlib.pyplot as plt

for i in range(1):
    print i
    ts1 = ts + np.sqrt(100.) * np.random.randn(len(ts))
    Ls1 = Ls + np.sqrt(1000.0) * np.random.randn(len(Ls))
    spl = UnivariateSpline(ts1, Ls1, k = 3, s =  0.01)
    ts_full = np.linspace(min(ts1), max(ts1),200)

    print max(ts1)
    print spl(max(ts1) + 1000.0)
    #plt.plot(ts_full, spl(ts_full), 'k')
    #plt.plot(ts1, Ls1, 'ro')

    #plt.plot(ts_full, spl.derivative()(ts_full), 'b')


plt.show()
