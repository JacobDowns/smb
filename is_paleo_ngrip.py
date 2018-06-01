from model.inputs.forward_paleo_inputs import *
from model.forward_model.forward_ice_model import *
import matplotlib.pyplot as plt


model_inputs = ForwardPaleoInputs('paleo_inputs/is_paleo_11_6_steady.hdf5', dt = 1./3., delta_temp_record = 'ngrip')
model = ForwardIceModel(model_inputs, "out", "paleo")

# Number of steps
N = 4500*3

ts = []
Ls = []

for i in range(N):
    ts.append(model_inputs.start_year + model.t)
    Ls.append(model.step())

plt.plot(ts, Ls)
plt.show()

np.savetxt('is_paleo/ngrip_ts1.txt', ts)
np.savetxt('is_paleo/ngrip_Ls1.txt', Ls)
