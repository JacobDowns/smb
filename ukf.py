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
        self.model = ForwardIceModel(inputs, "out", "L_dist")

        # SMB parameter mean
        self.adot0_mu = 0.50942564589
        # SMB parameter variance
        self.adot0_sigma2 = 1.
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
        # Process variance
        self.Q = 0.05


    # Process model
    def F(self, x):
        return x

    # Measurement Model
    def H(self, x):
        L = np.zeros(len(x))
        for i in range(len(x)):
            L[i] = self.model.try_step(self.dt, x[i])

        return L


    ### Add a little noise to the smb
    def predict(self):
        """
        Run the process model to get the prior. (Just adds noise.)
        """
        # Run sigma points through process model
        sigma_points = self.mwer_sigma.sigma_points(self.adot0_mu, self.adot0_sigma2)
        Y = self.F(sigma_points)
        # Prior mean
        x_bar = np.dot(self.mwer_sigma.mean_weights, Y)
        # Prior variance
        P_bar = np.dot(self.mwer_sigma.variance_weights, (Y - x_bar)**2) + self.Q

        return x_bar, P_bar, Y


    ### Update
    def step(self):
        self.t += 1.

        ### Compute state mean and covariance
        ########################################################################
        # Run process model to get the prior
        x_bar, P_bar, Y = self.predict()
        # Run the mesurement model
        L = self.H(Y)
        # Observation mean
        mu_z = np.dot(self.mwer_sigma.mean_weights, L)
        # Get the observation mean and variance
        z, R = self.get_obs(self.t)
        # Residual
        y = z - mu_z
        # Measurement variance
        P_z = np.dot(self.mwer_sigma.variance_weights, (L - mu_z)**2) + R
        # Kalman gain
        K = np.dot(self.mwer_sigma.variance_weights, (Y - x_bar)*(L - mu_z)) * (1. / P_z)
        # State mean
        x = x_bar + K*y
        # State variance
        P = P_bar - K*P_z*K

        ### Take a real step in the model using the "optimal" SMB param
        ########################################################################
        self.adot_mu = x
        self.adot_sigma2 = P
        L = self.model.try_step(self.dt, self.adot_mu, accept = True)

        print x, abs(z-L)
        return x, L, abs(z-L)




    # Mean and variance of observation at a given time
    def get_obs(self, t):
        mu = self.L_init + self.retreat_rate*t
        sigma = (2000.0*np.sin( 2.*np.pi*t / 2000.) + 500.0) / 2.

        return (mu, sigma**2)



    def sigma_points(self, mean, variance):
        points = np.array([mean - np.sqrt((1. + self.lam)*variance), mean, mean + np.sqrt((1. + self.lam)*variance)])
        return points

kalman = UKF()

adots = []
Ls = []
difs = []

for i in range(1000):
    adot, L, dif = kalman.step()
    adots.append(adot)
    difs.append(dif)
    Ls.append(L)

print adots
print
print Ls
print
print difs
plt.plot(adots)
plt.show()
