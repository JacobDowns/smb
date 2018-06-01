from model.inputs.forward_paleo_inputs import *
from model.forward_model.forward_ice_model import *
import matplotlib.pyplot as plt

"""
Force the ice sheet to retreat at a constant rate of speed.
"""

model_inputs = ForwardPaleoInputs('paleo_inputs/is_paleo_steady.hdf5', dt = 1./3.)
model = ForwardIceModel(model_inputs, "out", "paleo")


import numpy as np
import matplotlib.pyplot as plt
plt.rcParams.update({'font.size': 22})

### Setup plot
################################################################################

plt.ion()
fig,ax = plt.subplots(nrows=2,sharex=True,figsize=(7,7))
xs = model_inputs.mesh.coordinates() * model_inputs.L_init
L_init = model_inputs.L_init

bed = project(model.B)
surface = project(model.S0_c)
adot = project(model.adot_prime_func)
surface_ref = project(model_inputs.input_functions['S_ref'])

ph_bed, = ax[0].plot(xs, bed.compute_vertex_values(), 'b', linewidth = 2.5)
ph_surface, = ax[0].plot(xs, surface.compute_vertex_values(), 'k', linewidth = 2.5)
#ax[0].plot(xs, surface_ref.compute_vertex_values(), 'g', linewidth = 2.5)
ax[0].set_ylim(-400, 3500.)
ax[0].set_xlim(0, L_init)
ax[0].set_ylabel('S (m)')

ph_adot, = ax[1].plot(xs, adot.compute_vertex_values(), 'k', linewidth = 2.5)
ax[1].plot(xs, 0.*xs, 'b', linewidth = 2.5)
ax[1].set_ylim(-2.5, 0.75)
ax[1].set_xlim(0, L_init)
ax[1].set_xlabel('x (m)')
ax[1].set_ylabel('smb (m/a)')

N = 4100
dt = 0.5
dt_schedule = N*[dt]


for i in range(len(dt_schedule)):
    L = model.step(dt_schedule[i])

    if model.i % 20 == 0:
        xs = model_inputs.mesh.coordinates() * float(model.L0)

        # Plot thickness
        ax[0].set_xlim(0, L_init)
        surface = project(model.S0_c)
        ph_surface.set_xdata(xs)
        ph_surface.set_ydata(surface.compute_vertex_values())

        # Plot smb
        ax[1].set_xlim(0, L_init)
        adot = project(model.adot_prime_func)
        ph_adot.set_xdata(xs)
        ph_adot.set_ydata(adot.compute_vertex_values())

        plt.pause(0.000000000000000001)

#model.write_steady_file('paleo_inputs/inverse_start')
