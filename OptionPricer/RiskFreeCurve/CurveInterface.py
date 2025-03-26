import QuantLib as ql
import numpy as np
from RiskFreeCurve.CurveBuilder import CurveBuilder
from RiskFreeCurve.MarketDataFetcher import MarketDataFetcher
from RiskFreeCurve.RateInterpolator import RateInterpolator


class CurveInterface:
    """
    "Facade" class to orchestrate the construction of the risk-free yield curve:
    - Fetching data
    - Interpolation
    - QuantLib curve construction
    """

    def __init__(self, tickers: list[str], start_date, end_date):
        """
        Initializes and builds the full yield curve infrastructure
        
        1. Fetch market data (from yfinance)
        2. Fit a cubic spline interpolator to zero rates
        3. Build a QuantLib curve from instruments

        :param tickers: List of yfinance tickers (e.g., ["^IRX", "^FVX", "^TNX", "^TYX"])
        :param start_date: Start date for historical data (YYYY-MM-DD)
        :param end_date: End date for historical data (YYYY-MM-DD)
        """

        # 1. Fetching data
        market_data_fetcher = MarketDataFetcher(tickers, start_date, end_date)
        market_data_fetcher.fetch_data()
        maturities, rates = market_data_fetcher.get_latest_rates()

        # 2. Interpolation
        self.rate_interpolator = RateInterpolator(maturities, rates)
        self.rate_interpolator.fit_cubic_spline()
        self.grid = np.linspace(0.25, 30, 100)
        self.interp_rates = self.rate_interpolator.interpolate(self.grid)

        # 3. curve construction
        self.curve_builder = CurveBuilder()
        self.curve_builder.build_curve(maturities, rates)

    
    def infer(self, plot: float) -> tuple[float, float]:
        """
        Compute the discount factor and continuous-compounding zero rate 
        from the QuantLib curve for a given maturity in years.

        :param maturity: Target maturity in years (e.g. 2.0)
        :return: (discount factor, zero rate as decimal)
        """
        return (self.curve_builder.get_discount_factor(plot),
                self.curve_builder.get_zero_rate(plot, compounding=ql.Continuous))

    def plot_interpolation(self):
        """
        Plot the original rates and the cubic spline interpolation over a dense grid.
        """
        self.rate_interpolator.plot_interpolation(self.grid, self.interp_rates)
