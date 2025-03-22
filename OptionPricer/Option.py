import abc
from dataclasses import dataclass
from datetime import datetime

@dataclass
class Option(abc.ABC):
    """
    Abstract class to represent an option
    """
    S: float # underlying spot price
    r: float # constant risk-free rate
    sigma: float # constant volatility
    T: datetime # maturity
    K: float # strike


@dataclass
class Call(Option):
    """
    Class to represent a call option
    """

@dataclass
class Put(Option):
    """
    Class to represent a put option
    """