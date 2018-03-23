from model.inputs import *
from model.adot_inputs_elevation_dependent import *
from model.forward_model.forward_ice_model import *
import matplotlib.pyplot as plt
from filterpy.kalman import MerweScaledSigmaPoints
from sigma_points import *


adot_inputs = AdotInputsElevationDependent()
inputs = Inputs('is_steady_elevation_dependent_width.hdf5', adot_inputs)
model = ForwardIceModel(inputs, "out", "L_dist")


"""
Force the ice sheet to retreat at a constant rate of speed.
"""

"""



adot0s = np.sqrt(0.05) * np.random.randn(2000) + 0.50942564589

Ls = []

i = 0
for adot0 in adot0s:
    print i
    Ls.append(model.try_step(1., adot0))
    i += 1



Ls = np.array(Ls)

plt.hist(Ls - inputs.L_init, bins='auto')
plt.show()


print Ls.mean()
print np.var(Ls)

quit()

"""


points = SigmaPointsScalar(alpha = 0.1, beta = 2., kappa = 2.)

sigma_points = points.sigma_points(0.50942564589, 0.05)

#print points.mean_weights
#print
#print points.variance_weights


Ls = []
for adot0 in sigma_points:
    print adot0
    Ls.append(model.try_step(1., adot0))

Ls = np.array(Ls)

mean = np.dot(points.mean_weights, np.array(Ls))
variance = np.dot(points.variance_weights, (Ls - mean)**2)

print mean
print variance

mu = 0.0 #mean
#variance = 1
sigma = np.sqrt(variance)
x = np.linspace(mu - 3*sigma, mu + 3*sigma, 100)
plt.plot(x,plt.mlab.normpdf(x, mu, sigma))
plt.show()
#print Ls"""
