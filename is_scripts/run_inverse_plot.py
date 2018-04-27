from model.inverse_inputs import *
from model.length_inputs_linear import *
from model.adot_inputs_elevation_dependent import *
from model.inverse_model.inverse_ice_model import *

"""
Force the ice sheet to retreat at a constant rate of speed.
"""

adot_inputs = AdotInputsElevationDependent()
length_inputs = LengthInputsLinear(-25.)

inputs = InverseInputs('is_steady_elevation_dependent.hdf5', adot_inputs, length_inputs, dt = 1., N = 6000)
model = InverseIceModel(inputs, "out", "replay/is_replay_retreat")

import numpy as np
import matplotlib.pyplot as plt
plt.rcParams.update({'font.size': 22})

### Setup plot
################################################################################

plt.ion()
fig,ax = plt.subplots(nrows=2,sharex=True,figsize=(7,7))
xs = inputs.mesh.coordinates()
L_init = inputs.L_init

surface = project(model.S)
bed = project(model.B)
adot = project(model.adot_prime_func)

ph_bed, = ax[0].plot(xs, bed.compute_vertex_values(), 'b', linewidth = 2.5)
ph_surface, = ax[0].plot(xs, surface.compute_vertex_values(), 'k', linewidth = 2.5)
ax[0].set_xlim(0., 1.)
ax[0].set_ylim(-550, 3500)


ph_adot, = ax[1].plot(xs, adot.compute_vertex_values(), 'k', linewidth = 2.5)
ax[1].plot(xs, 0.0 * xs, 'b', linewidth = 2.5)
ax[1].set_ylim(-3., 0.75)
ax[0].set_xlim(0., 1.)

plt.pause(0.00000001)



print model.N

while model.i < model.steps:
    print model.i
    model.step()

    if model.i % 10 == 0:

        # Plot thickness
        surface = project(model.S)
        bed = project(model.B)

        ph_surface.set_xdata(xs)
        ph_surface.set_ydata(surface.compute_vertex_values())

        ph_bed.set_xdata(xs)
        ph_bed.set_ydata(bed.compute_vertex_values())

        # Plot smb
        #ax[1].set_xlim(0, float(model.L0))
        adot = project(model.adot_prime_func)
        ph_adot.set_xdata(xs)
        ph_adot.set_ydata(adot.compute_vertex_values())

        plt.pause(0.000000000000000001)
