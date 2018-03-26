import numpy as np

"""
Abstract representation of a gaussian pdf.
"""

class GaussianRandomVariable(object):

    def __init__(self, mu, sigma2):
        self.mu = mu
        self.sigma2 = sigma2


    # Add a random variable to the current random variable with this distribution
    def add(self, g):
        self.mu = self.mu + g.mu
        self.sigma2 = self.sigma2 + g.sigma2


    # Multiply a random variable with this distribution by another random variable
    def multiply(self, g):
        self.mu = (self.simgma2*g.mu + g.sigma2*self.mu) / (self.sigma2 + g.sigma2)
        self.sigma2 = (self.sigma2*g.sigma2) / (self.sigma2 + g.sigma2)
