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
    nb_samples = 100_000
    print("Monte Carlo", pricer_monte_carlo.calculate(nb_samples))