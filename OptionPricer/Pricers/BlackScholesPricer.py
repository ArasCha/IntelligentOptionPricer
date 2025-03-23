from numpy import exp
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
        
        if isinstance(self.instrument, Call):
            return self.S * exp(-self.q*self.T) * norm.cdf(self.d1) - self.K * exp(-self.r*self.T) * norm.cdf(self.d2)

        elif isinstance(self.instrument, Put):
            return -self.S * exp(-self.q*self.T) * norm.cdf(-self.d1) + self.K * exp(-self.r*self.T) * norm.cdf(-self.d2)
