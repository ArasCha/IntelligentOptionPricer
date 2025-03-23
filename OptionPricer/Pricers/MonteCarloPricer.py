from Option import Call, Put
import numpy as np
from Pricers.Pricer import Pricer

from scipy.stats import norm
from scipy.stats.qmc import Sobol



class MonteCarloPricer(Pricer):
    """
    Calculator of the today price of an european option with Monte Carlo
    """

    def calculate(self, nb_samples: int) -> float:
        """
        Calculate the price of the option with simple Monte Carlo
        """
        
        W_T = np.sqrt(self.T) * np.random.normal(size=nb_samples) # W_T \sim \sqrt{T}\mathcal{N}(0,1)
        S_T = self.S * np.exp( (self.r - self.q - 0.5 * self.sigma**2) * self.T + self.sigma * W_T) # vector of size nb_samples. Solution of the Black-Scholes EDS
        
        return np.mean(self.payoff(S_T) * np.exp(-self.r * self.T))


    def calculate_qmc(self, nb_samples: int) -> float:
        """
        Calculate the price of the option with Quasi-Monte Carlo with a Sobol sequence
        """

        sampler = Sobol(d=1, scramble=True) # d=1 cause we need 1 dimension. Scramble=True to introduce randomness into the sequence without destroying the low-discrepancy
        U = sampler.random(nb_samples).flatten() # generate the sequence, \sim U([0, 1]). Better uniformity if nb_samples is a power of 2

        G = norm.ppf(U) # map U([0,1]) samples to N(0,1) via the inverse of the repartition function

        W_T = np.sqrt(self.T) * G
        
        W_T = np.sqrt(self.T) * np.random.normal(size=nb_samples) # W_T \sim \sqrt{T}\mathcal{N}(0,1)
        S_T = self.S * np.exp( (self.r - self.q - 0.5 * self.sigma**2) * self.T + self.sigma * W_T) # vector of size nb_samples. Solution of the Black-Scholes EDS
        
        return np.mean(self.payoff(S_T) * np.exp(-self.r * self.T))


    def calculate_antithetic(self, nb_samples: int) -> float:
        """
        Calculate the price of the option with antithetic variables
        """
        
        W_T = np.sqrt(self.T) * np.random.normal(size=nb_samples)
        drift = (self.r - self.q - 0.5 * self.sigma**2) * self.T
        S_T1 = self.S * np.exp( drift + self.sigma * W_T)
        S_T2 = self.S * np.exp( drift + self.sigma * -W_T) # antithetic of S_T1

        payoff = ( self.payoff(S_T1) + self.payoff(S_T2) )/2

        return np.mean(payoff * np.exp(-self.r * self.T))
