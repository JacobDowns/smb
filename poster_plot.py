from model.inputs.inverse_inputs import *
from model.inputs.adot_inputs_elevation_dependent import *
from model.inverse_model.inverse_ice_model import *
from scipy.interpolate import UnivariateSpline
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d

plt.rcParams.update({'font.size': 22})


### Linearly interpolate between moraine postions
####################################################################

moraine_ts = np.loadtxt('is_paleo/moraine_ts.txt')
print moraine_ts
moraine_Ls = np.loadtxt('is_paleo/moraine_Ls.txt')
moraine_ts -= moraine_ts[0]
ts = np.linspace(moraine_ts.min(), moraine_ts.max(), 100)
L_offset =  UnivariateSpline(ts, np.interp(ts, moraine_ts, moraine_Ls - moraine_Ls[0]), k = 2, s =  0.01)


### Define model inputs
####################################################################
adot_inputs = AdotInputsElevationDependent()
inputs = InverseInputs('paleo_inputs/inverse_steady.hdf5', L_offset, L_offset.derivative(), adot_inputs)
model = InverseIceModel(inputs, 'out')


profiles = np.loadtxt('poster_plot/profiles.txt')
Ls = np.loadtxt('poster_plot/Ls.txt')
adots = np.loadtxt('poster_plot/adots.txt')

plt.plot(adots, 'ko-')
plt.show()

quit()

print profiles
model.update_inputs(inputs.L_init, 0., 1./3.)
B_init = model.B.vector().get_local()
L_init = inputs.L_init


coords = model.mesh.coordinates()[:][:,0]
print B_init
print L_init
print coords

plt.plot(coords*L_init, B_init[::-1], linewidth = 4)


indexes = (moraine_ts/100).astype(int)
indexes[-1] = 42


[-11600. -10200.  -9200.  -8200.  -7300.]
labels = ['-11.6 ka', '-10.2 ka', '-9.2 ka', '-8.2 ka', '-7.3 ka']
colors = ['k', 'r', 'g', 'y', 'c']

j = 0
for i in indexes:
    L = Ls[i]
    profile = profiles[i,:]
    plt.plot(coords*L, profile[::-1], colors[j], linewidth = 3, label = labels[j])
    j += 1

plt.xlabel('x (m)')
plt.ylabel('Elevation (m)')
plt.xlim(0., L_init)
plt.legend()
plt.show()


quit()





                               
