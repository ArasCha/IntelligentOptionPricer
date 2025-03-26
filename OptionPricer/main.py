from Pricers.BlackScholesPricer import BlackScholesPricer
from Pricers.MonteCarloPricer import MonteCarloPricerAntithetic, MonteCarloPricerClassic, MonteCarloPricerLazy, MonteCarloPricerQMC
from Pricers.Pricer import Pricer
from Option import Call, Put
from VolatilitySurface import ImpliedVolSurfaceBuilder
from RiskFreeCurve.CurveInterface import CurveInterface



if __name__ == "__main__":

    instrument = Call(maturity="04/22/2025",
                    rate= 0.1,
                    strike= 100,
                    underlying_price= 150,
                    volatility= 0.2,
                    dividend= 0.04)

    # pricer_black_scholes = BlackScholesPricer(instrument)
    # print("Black-Scholes: ", pricer_black_scholes.calculate())

    # pricer_monte_carlo = MonteCarloPricer(instrument)
    # nb_samples = 2**18 # power of 2 for Sobol sequence in qmc
    # print("Monte Carlo calculate", pricer_monte_carlo.calculate(nb_samples))
    # print("Monte Carlo calculate_qmc", pricer_monte_carlo.calculate_qmc(nb_samples))
    # print("Monte Carlo calculate_antithetc", pricer_monte_carlo.calculate_antithetic(nb_samples))
    # print("Monte Carlo calculate_lazy", pricer_monte_carlo.calculate_lazy(nb_samples))

    # print(pricer_monte_carlo.benchmark(10000))

    # ImpliedVolSurfaceBuilder("AAPL").plot_surface()

    pricers: list[Pricer] = [
        MonteCarloPricerQMC(instrument),
        MonteCarloPricerAntithetic(instrument),
        MonteCarloPricerClassic(instrument),
        MonteCarloPricerLazy(instrument),
        BlackScholesPricer(instrument)
    ]

    results = {}
    for pricer in pricers:
        time, price = pricer.benchmark(10000)
        results[pricer.__class__.__name__] = {
            "time": time,
            "price": price
        }
    print(results)
        



    # tickers = ["^IRX", "^FVX", "^TNX", "^TYX"]  # 3 mois, 5 ans, 10, 30
    # start_date = "2023-01-01"
    # end_date = "2023-03-01"

    # curve = CurveInterface(tickers, start_date, end_date)
    # for plot in [0.25, 1, 2, 5, 10, 20, 30]:
    #     discount_factor, zero_rate = curve.infer(plot)
    #     print(f"Maturity {plot:5.2f} yrs | DF = {discount_factor:6.4f} | ZeroRate cont. = {zero_rate * 100:4.2f}%")
