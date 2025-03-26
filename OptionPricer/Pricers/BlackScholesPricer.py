from numpy import exp, log, sqrt
from Option import Call, Put
from scipy.stats import norm
from Pricers.Pricer import Pricer
import numpy as np
import time





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

    def benchmark(self, nb_samples):
        """
        Benchmark the performance of the `calculate` method of the pricer.
        Runs the `calculate` method 1000 times.

        Args:
            nb_samples (int): The number of samples to pass to the `calculate` function.

        Returns:
            tuple: A tuple containing:
                - The average execution time (in seconds), rounded to 6 decimal places.
                - The calculated price, rounded to 6 decimal places.
        """

        durations = np.empty(1000)

        for i in range(1000):
            start = time.perf_counter()
            price = self.calculate()
            durations[i] = time.perf_counter() - start

        return (round(float(np.mean(durations)), 6), round(price, 6))