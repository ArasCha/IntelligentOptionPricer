from Pricers.BlackScholesPricer import BlackScholesPricer
from Option import Call, Put



if __name__ == "__main__":

    instrument = Call(maturity="04/22/2025",
                    rate= 0.1,
                    strike= 100,
                    underlying_price= 150,
                    volatility= 0.2)

    pricer = BlackScholesPricer(instrument)
    price = pricer.calculate()
    print(price)