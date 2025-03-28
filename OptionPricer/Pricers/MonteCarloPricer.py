import abc
from Option import Call, Put
import numpy as np
from Pricers.Pricer import Pricer


from scipy.stats import norm
from scipy.stats.qmc import Sobol
import time


class MonteCarloPricer(Pricer):
    """
    Abstract Monte Carlo Pricer
    """

    @abc.abstractmethod
    def calculate(self) -> float:
        """
        Calculate the price of the option with abstract Monte Carlo
        """

    def benchmark(self, nb_samples: int):
        """
        Benchmark the performance of the `calculate` method of the pricer.
        Runs the `calculate` method 1000 times.

        Args:
            nb_samples (int): The number of samples to pass to the `calculate` function.

        Returns:
            tuple: A tuple containing:
                - The average execution time (in seconds), rounded to 6 decimal places.
                - The average calculated price, rounded to 6 decimal places.
        """
        nb_iterations = 1000
        durations = np.empty(nb_iterations)
        prices = np.empty(nb_iterations)

        for i in range(nb_iterations):
            start = time.perf_counter()
            prices[i] = self.calculate(nb_samples)
            durations[i] = time.perf_counter() - start

        return (round(float(np.mean(durations)), 6), round(float(np.mean(prices)), 6))


class MonteCarloPricerClassic(MonteCarloPricer):
    """
    Calculator of the today price of an european option with classic Monte Carlo
    """

    def calculate(self, nb_samples: int) -> float:
        """
        Calculate the price of the option with simple Monte Carlo
        """
        
        W_T = np.sqrt(self.T) * np.random.normal(size=nb_samples) # W_T \sim \sqrt{T}\mathcal{N}(0,1)
        S_T = self.S * np.exp( (self.r - self.q - 0.5 * self.sigma**2) * self.T + self.sigma * W_T) # vector of size nb_samples. Solution of the Black-Scholes EDS
        
        return np.mean(self.payoff(S_T) * np.exp(-self.r * self.T))


class MonteCarloPricerQMC(MonteCarloPricer):
    """
    Calculator of the price of the option with Quasi-Monte Carlo with a Sobol sequence
    """
    
    def calculate(self, nb_samples: int) -> float:
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


class MonteCarloPricerAntithetic(MonteCarloPricer):
    """
    Calculator of the price of the option with antithetic variables
    """
    
    def calculate(self, nb_samples: int) -> float:
        """
        Calculate the price of the option with antithetic variables
        """
        
        W_T = np.sqrt(self.T) * np.random.normal(size=nb_samples)
        drift = (self.r - self.q - 0.5 * self.sigma**2) * self.T
        S_T1 = self.S * np.exp( drift + self.sigma * W_T)
        S_T2 = self.S * np.exp( drift + self.sigma * -W_T) # antithetic of S_T1

        payoff = ( self.payoff(S_T1) + self.payoff(S_T2) )/2

        return np.mean(payoff * np.exp(-self.r * self.T))


class MonteCarloPricerLazy(MonteCarloPricer):
    """
    Monte Carlo price of the option with a lazy random generator
    Uses batches of gaussian random variables
    """

    def calculate(self, nb_samples: int, batch_size: int = 100_000) -> float:
        """
        Monte Carlo price of the option with a lazy random generator
        Uses batches of gaussian random variables
        """
        drift = (self.r - self.q - 0.5 * self.sigma**2) * self.T

        def _normal_generator(batch_size: int):
            while True:
                yield np.random.normal(size=batch_size)

        gen = _normal_generator(batch_size) # lazy generator

        sum_payoff = 0.0
        count_draws = 0

        while count_draws < nb_samples:

            G = next(gen) # batch of random gaussian variables

            needed = nb_samples - count_draws # how many more samples we need to reach nb_samples

            if len(G) > needed: # If the batch from the generator is larger than the amount we still need
                G = G[:needed] # truncate the batch to exactly 'needed' samples

            S_T = self.S * np.exp(drift + self.sigma * np.sqrt(self.T) * G)

            sum_payoff += self.payoff(S_T).sum()
            count_draws += len(G)

        return (sum_payoff / nb_samples) * np.exp(-self.r * self.T)
