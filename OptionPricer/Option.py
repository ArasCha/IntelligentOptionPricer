import abc
from dataclasses import dataclass
from datetime import datetime

@dataclass
class Option(abc.ABC):
    """
    Abstract class to represent an option
    """
    underlying_price: float # underlying spot price
    rate: float # constant risk-free rate
    volatility: float # constant volatility
    maturity: datetime # expected format: "%m/%d/%Y"
    strike: float
    dividend: float # constant dividend

    def __post_init__(self):
        """
        Checks whether entered parameters meet Black-Scholes hypothesis
        and transforms maturity into datetime if needed
        """
        assert self.volatility >= 0, "Volatility must be positive"
        assert self.underlying_price >= 0, "Underlying price must be positive"
        assert self.dividend >= 0, "Dividend must be positive"

        if type(self.maturity) == str:
            self.maturity = datetime.strptime(self.maturity, '%m/%d/%Y')
            assert self.maturity > datetime.today(), "Maturity date must be greater than calculation date"



class Call(Option):
    """
    Class to represent a call option
    """

class Put(Option):
    """
    Class to represent a put option
    """