from Pricers.BlackScholesPricer import BlackScholesPricer
from Pricers.MonteCarloPricer import MonteCarloPricerAntithetic, MonteCarloPricerClassic, MonteCarloPricerLazy, MonteCarloPricerQMC
from Pricers.Pricer import Pricer
from Option import Call, Put



if __name__ == "__main__":

    instrument = Call(maturity="04/22/2025",
                    rate= 0.1,
                    strike= 100,
                    underlying_price= 150,
                    volatility= 0.2,
                    dividend= 0.04)


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
