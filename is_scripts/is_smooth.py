from model.smooth_replay import *
from model.adot_inputs_elevation_dependent import *

"""
Smooth the climate, whatever that means.
"""

adot_inputs = AdotInputsElevationDependent()
SmoothReplay('out/replay/is_replay_retreat.hdf5', adot_inputs, 'out/replay/is_replay_retreat_smooth_3001', window = 3001)
