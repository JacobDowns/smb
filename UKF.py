from model.inputs import *
import numpy as np
from model.adot_inputs_elevation_dependent import *
from model.forward_model.forward_ice_model import *
import matplotlib.pyplot as plt
from sigma_points import *

"""
Simple unscented Kalman filter
"""

class UKF(object):

    def __init__(self):

        ### Setup the model
        adot_inputs = AdotInputsElevationDependent()
        inputs = Inputs('is_steady_elevation_dependent_width.hdf5', adot_inputs)
        model = ForwardIceModel(inputs, "out", "L_dist")

        # SMB parameter mean
        self.adot0_mu = 0.50942564589
        # SMB parameter variance
        self.adot0_sigma2 = 0.000000001
        # Initial time
        self.t = 0.0
        # Time step
        self.dt = 1.
        # Initial margin position
        self.L_init = inputs.L_init
        # Expected approximate rate of retreat
        self.retreat_rate = -25.
        # Object for calculating sigma points
        self.mwer_sigma = SigmaPointsScalar(alpha = 0.1, beta = 2., kappa = 2.)

        self.Y = None

    # Process model
    def F(self, x):
        return x

    # Measurement Model
    def H(self, x):
        L = np.zeros(len(x))
        for i in range(len(x)):
            L[i] = model.try_step(self.dt, x)


    ### Add a little noise to the smb
    def predict(self):
        """
        Run the process model to get the prior. (Just adds noise.)
        """

        # Run sigma points through process model
        sigma_points = self.mwer_sigma.sigma_points(self.adot0_mu, self.adot0_sigma2)
        Y = self.F(sigma_points)
        # Prior mean
        adot0_mu = np.dot(self.mwer_sigma.mean_weights, Y)
        # Prior covariance
        adot0_sigma2 = np.dot(self.mwer_sigma.variance_weights, (Y - adot0_mu)**2) + 0.1

        return adot0_mu, adot0_sigma2, Y


    ### Update
    def step(self):
        self.t += 1.

        x_bar, P_bar, Y = self.predict()

        print x_bar, P_bar, Y

        """
        Ls = []
        for adot0 in sigma_points:
            Ls.append(model.try_step(1., adot0))

        Ls = np.array(Ls)
        # Measurement mean
        L_mu = np.dot(self.sigma_point_generator.mean_weights, np.array(Ls))
        # Observation mean and variance
        (L_obs_mu, L_obs_sigma2) = self.get_obs(self.t)
        # Residual
        y = obs_mu - L_mu
        # Measurement covariance
        L_sigma2 = np.dot(self.sigma_point_generator.variance_weights, (Ls - L_mu)**2) + L_obs_sigma2
        # Kalman gain
        adot0_mu = self.belief.mu
        K = np.dot(self.sigma_point_generator.variance_weights, (sigma_points - adot0_mu)*(Ls - L_mu)) * (1. / L_sigma2)

        adot0_mu += K*y



        # Residual
        y = L_obs.mu - L_mu"""


    # Return a random variable representing the observation at the given time
    def get_obs(self, t):


        ### Compute the mean and variance of the observation at the current time
        mu = self.L_init + self.retreat_rate*t
        sigma = (1500.0*np.sin( 2.*np.pi*t / 2000.) + 250.0) / 2.

        return (mu, sigma**2)



    def sigma_points(self, mean, variance):
        points = np.array([mean - np.sqrt((1. + self.lam)*variance), mean, mean + np.sqrt((1. + self.lam)*variance)])
        return points

kalman = KalmanFilter()
kalman.step()
