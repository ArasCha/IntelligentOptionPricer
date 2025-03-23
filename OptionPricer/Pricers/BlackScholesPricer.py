from numpy import exp, log, sqrt
from Option import Call, Put
from scipy.stats import norm
from Pricers.Pricer import Pricer





class BlackScholesPricer(Pricer):
    """
    Calculator of the today price of an european option based on the Black-Scholes model
    """

    def calculate(self) -> float:
        """
        Calculate the price of the option
        """
        d1 = (log(self.S/self.K) + self.r*self.T + 0.5*self.T*self.sigma**2) / (self.sigma*sqrt(self.T))
        d2 = d1 - self.sigma*sqrt(self.T)
        
        if isinstance(self.instrument, Call):
            return self.S * exp(-self.q*self.T) * norm.cdf(d1) - self.K * exp(-self.r*self.T) * norm.cdf(d2)

        elif isinstance(self.instrument, Put):
            return -self.S * exp(-self.q*self.T) * norm.cdf(-d1) + self.K * exp(-self.r*self.T) * norm.cdf(-d2)
