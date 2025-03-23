from Pricers.BlackScholesPricer import BlackScholesPricer
from Pricers.MonteCarloPricer import MonteCarloPricer
from Option import Call, Put



if __name__ == "__main__":

    instrument = Call(maturity="04/22/2025",
                    rate= 0.1,
                    strike= 100,
                    underlying_price= 150,
                    volatility= 0.2,
                    dividend= 0.04)

    pricer_black_scholes = BlackScholesPricer(instrument)
    print("Black-Scholes: ", pricer_black_scholes.calculate())

    pricer_monte_carlo = MonteCarloPricer(instrument)
    nb_samples = 2**18 # power of 2 for Sobol sequence in qmc
    print("Monte Carlo calculate", pricer_monte_carlo.calculate(nb_samples))
    print("Monte Carlo calculate_qmc", pricer_monte_carlo.calculate_qmc(nb_samples))
    print("Monte Carlo calculate_antithetc", pricer_monte_carlo.calculate_antithetic(nb_samples))
    print("Monte Carlo calculate_lazy", pricer_monte_carlo.calculate_lazy(nb_samples))

    print(pricer_monte_carlo.benchmark(10000))