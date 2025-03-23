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
