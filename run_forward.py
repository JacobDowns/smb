from model.forward_inputs import *
from model.forward_model.forward_ice_model import *

forward_inputs = ForwardInputs('out/replay_retreat.hdf5')
model = ForwardIceModel(forward_inputs, "out", "forward")

ts = []
Ls = []

while model.i < model.N:
    ts.append(model.t)
    Ls.append(float(model.L0))
    model.step()
    plot(model.H0)



import numpy as np
import matplotlib.pyplot as plt

plt.rcParams.update({'font.size': 22})

ts = np.array(ts)
Ls = np.array(Ls)

plt.plot(ts, Ls, 'r', linewidth = 2.5, label = 'model')
#Ls1 = forward_inputs.L_init +  (1. / 100.0) * np.array(ts)**2
#Ls1 = forward_inputs.L_init - 10.*ts
C = (2.*np.pi) / 1000.0
M = 7500.0
Ls1 = forward_inputs.L_init + M * np.sin(C * ts)

plt.plot(ts, Ls1, 'k--', linewidth = 2.5, label = 'exact')
plt.xlabel('t')
plt.ylabel('L')
plt.legend(loc = 2)
plt.show()

#model = InverseIceModel(inverse_inputs, "out", "replay")
#model.run(0.25, 4000)
