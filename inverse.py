from model.inputs.inverse_inputs import *
from model.inputs.adot_inputs_elevation_dependent import *
from model.inverse_model.inverse_ice_model import *
from scipy.interpolate import UnivariateSpline
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d


### Linearly interpolate between moraine postions
####################################################################

moraine_ts = np.loadtxt('is_paleo/moraine_ts.txt')
moraine_Ls = np.loadtxt('is_paleo/moraine_Ls.txt')
moraine_ts -= moraine_ts[0]
ts = np.linspace(moraine_ts.min(), moraine_ts.max(), 100)
L_offset =  UnivariateSpline(ts, np.interp(ts, moraine_ts, moraine_Ls - moraine_Ls[0]), k = 2, s =  0.01)


### Define model inputs
####################################################################
adot_inputs = AdotInputsElevationDependent()
inputs = InverseInputs('paleo_inputs/inverse_steady.hdf5', L_offset, L_offset.derivative(), adot_inputs)
model = InverseIceModel(inputs, 'out')

Ls = []
profiles = []
adot_profiles = []

adots = []
for i in range(4299*3):
    adot0, L = model.step(1./3.)
    adots.append(adot0)

    if i % (100*3) == 0 or i == 4299*3:
        print
        print
        surf = project(model.B + model.H0_c, model.V_cg)
        profiles.append(surf.vector().get_local())
        adot_profiles.append(model.adot_prime_func.vector().get_local())
        Ls.append(L)
        
print np.array(profiles)
print Ls

np.savetxt('poster_plot/profiles.txt', np.array(profiles))
np.savetxt('poster_plot/Ls.txt', np.array(Ls))
np.savetxt('poster_plot/adots.txt', np.array(adots))
np.savetxt('poster_plot/adot_profiles.txt', np.array(adot_profiles))

quit()
plt.plot(adots)
plt.show()

print adots


                               
