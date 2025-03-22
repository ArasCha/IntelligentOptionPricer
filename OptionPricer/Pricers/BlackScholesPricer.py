from typing import Union
from numpy import sqrt, exp, log
from Option import Call, Put
from scipy.stats import norm
from datetime import datetime



CONVENTION_YEAR_FRACTION = 365
        


class BlackScholesPricer:
    """
    Calculator of the today price of an european option based on the Black-Scholes model
    """

    def __init__(self, instrument: Union[Call, Put]):
        self.instrument = instrument
        calculation_date = datetime.today()

        assert isinstance(instrument, Call) or isinstance(instrument, Put), f"{self.instrument} is not recognized as a Call or Put option"
        assert instrument.maturity > calculation_date, "Maturity date must be greater than calculation date"

        self.S = instrument.underlying_price
        self.K = instrument.strike
        self.r = instrument.rate
        self.sigma = instrument.volatility
        self.T = (instrument.maturity - calculation_date).days / CONVENTION_YEAR_FRACTION # time to maturity as a year fraction
        self.d1 = (log(self.S/self.K) + self.r*self.T + 0.5*self.T*self.sigma**2) / (self.sigma*sqrt(self.T))
        self.d2 = self.d1 - self.sigma*sqrt(self.T)


    def calculate(self) -> float:
        """
        Calculate the price of the option
        """
        
        if isinstance(self.instrument, Call):
            return self.S*norm.cdf(self.d1) - self.K * exp(-self.r*self.T) * norm.cdf(self.d2)

        elif isinstance(self.instrument, Put):
            return -self.S*norm.cdf(-self.d1) + self.K * exp(-self.r*self.T) * norm.cdf(-self.d2)
