from model.inverse_inputs import *
from model.length_inputs_linear import *
from model.adot_inputs_elevation_dependent import *
from model.inverse_model.inverse_ice_model import *

"""
Replay forward inputs (replays an inverse model run in the forwrad model.)
"""

# Times
ts = np.array([0.0, 1000., 2000., 3000., 4000., 5000., 6000.])
offsets = ts * (150e3 / 6000)

print ts
print offsets
