from model.inputs.forward_paleo_inputs import *
from model.forward_model.forward_ice_model import *
import matplotlib.pyplot as plt


model_inputs = ForwardPaleoInputs('paleo_inputs/is_paleo_11_6_steady.hdf5', dt = 1./3., delta_temp_record = 'buizert')
model = ForwardIceModel(model_inputs, "out", "paleo")

# Number of steps
N = 3600*3

ts = []
Ls = []
adot_ints = []

for i in range(N):
    ts.append(model_inputs.start_year + model.t)
    L = model.step()
    Ls.append(L)
    adot_int = assemble(model.adot_prime_func*dx)
    adot_ints.append(adot_int)
    print "adot int", adot_int

#plt.plot(ts, Ls)
#plt.show()
np.savetxt('is_paleo/buizert_adot_int1.txt', adot_ints)
np.savetxt('is_paleo/buizert_ts1.txt', ts)
np.savetxt('is_paleo/buizert_Ls1.txt', Ls)
