from typing import Union
import numpy as np
from Option import Call, Put
from datetime import datetime
import abc



CONVENTION_YEAR_FRACTION = 365
        


class Pricer(abc.ABC):
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
        self.q = instrument.dividend
        self.sigma = instrument.volatility
        self.T = (instrument.maturity - calculation_date).days / CONVENTION_YEAR_FRACTION # time to maturity as a year fraction

        if isinstance(instrument, Call):
            self.payoff = lambda S_T: np.maximum(S_T - self.K, 0)
        elif isinstance(instrument, Put):
            self.payoff = lambda S_T: np.maximum(self.K - S_T, 0)

    @abc.abstractmethod
    def calculate(self) -> float:
        """
        Calculate the price of the option
        """