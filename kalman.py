from model.inputs import *
import numpy as np
from model.adot_inputs_elevation_dependent import *
from model.forward_model.forward_ice_model import *
import matplotlib.pyplot as plt
from sigma_points import *

"""
Computes sigma points for a scalar Gaussian.
"""

class KalmanFilter(object):

    def __init__(self, alpha, beta, kappa):

        ### Setup the model
        adot_inputs = AdotInputsElevationDependent()
        inputs = Inputs('is_steady_elevation_dependent_width.hdf5', adot_inputs)
        model = ForwardIceModel(inputs, "out", "L_dist")

        ### Initial distribution for adot param
        self.adot0_mean = 0.50942564589
        self.adot_variance = 0.0001
        # Initial time
        self.t = 0.0
        # Time step
        self.dt = 1.


    ### Add a little noise to the smb
    def predict(self):
        """
        Our belief is that the climate should change very little over one time step,
        so add some noise to the adot0 parameter with mean 0 and small variance.
        """

        self.adot_variance = self.adot_variance + 0.1


    ### Update
    def update(self):

        ### Run the sigma points through the measruement model
        points = SigmaPointsScalar(alpha = 0.1, beta = 2., kappa = 2.)
        sigma_points = points.sigma_points(0.self.adot0_mean, self.adot0_variance)

        Ls = []
        for adot0 in sigma_points:
            Ls.append(model.try_step(1., adot0))

        ### Compute the mean and variance of the distribution we get from the

        Ls = np.array(Ls)
        L_mean = np.dot(points.mean_weights, np.array(Ls))
        L_variance = np.dot(points.variance_weights, (Ls - L_mean)**2)




    def sigma_points(self, mean, variance):
        points = np.array([mean - np.sqrt((1. + self.lam)*variance), mean, mean + np.sqrt((1. + self.lam)*variance)])
        return points
