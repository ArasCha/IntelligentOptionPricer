
import yfinance as yf
import numpy as np
from scipy.interpolate import interp1d
import plotly.graph_objects as go
import QuantLib as ql



class MarketDataFetcher:
    """
    Handles rate data fetching from Yahoo Finance,
    and prepares the latest available rate values for the most recent date.
    """

    def __init__(self, tickers, start_date, end_date):
        """
        :param tickers: List of Yahoo Finance tickers, e.g. ["^IRX", "^FVX", "^TNX", "^TYX"].
        :param start_date: Start date in format "YYYY-MM-DD".
        :param end_date:   End date in format "YYYY-MM-DD".
        """
        self.tickers = tickers
        self.start_date = start_date
        self.end_date = end_date
        self._data = None
        self._last_date = None

    def fetch_data(self):
        """
        Downloads market data for the selected tickers,
        stores the associated DataFrame in self._data and records the last available date.
        """
        self._data = yf.download(self.tickers, start=self.start_date, end=self.end_date, progress=False)
        if self._data is not None and not self._data.empty:
            self._last_date = self._data.index[-1]
        else:
            raise ValueError("No data retrieved for the specified period.")

    
    def get_latest_rates(self):
        """
        Extracts the latest interest rate points (in percentage) and converts them to decimal.
        :return: (maturities, rates) as (np.array, np.array).
        """
        assert self._data is not None, "fetch_data() method must be first."

        # Select the DataFrame with closing prices
        adj_close = self._data['Close'].copy()

        # Retrieve the rates (in %) at the last date
        last_rates_percent = adj_close.loc[self._last_date, self.tickers]

        # Convert to decimal
        last_rates_decimal = last_rates_percent / 100.0

        # Define our maturities (approx.) in years
        # Corresponding to tickers: ^IRX (3 months), ^FVX (5 years), ^TNX (10 years), ^TYX (30 years)
        maturities = np.array([0.25, 5.0, 10.0, 30.0])
        rates = last_rates_decimal.values

        return maturities, rates

    @property
    def last_date(self):
        return self._last_date



class RateInterpolator:
    """
    Handles interpolation of zero-coupon rates using a cubic spline (or other).
    """

    def __init__(self, maturities, rates):
        """
        :param maturities: Maturities in years (numpy array or list).
        :param rates: Zero-coupon rates in decimal (numpy array or list).
        """
        self.maturities = maturities
        self.rates = rates
        self.spline = None

    def fit_cubic_spline(self):
        """
        Builds a cubic spline (interp1d) based on the (maturities, rates) points.
        """
        self.spline = interp1d(
            self.maturities, 
            self.rates, 
            kind='cubic', 
            fill_value="extrapolate"
        )

    
    def interpolate(self, grid_points):
        """
        Returns interpolated rates for a set of specified points.
        :param grid_points: List or array of maturities for which we want to calculate the rate.
        :return: Numpy array of interpolated rates.
        """
        assert self.spline is not None, "Spline not defined, call fit_cubic_spline() first."
        return self.spline(grid_points)
    

    def plot_interpolation(self, grid_points, interpolated_rates):
        """
        Displays the interpolation curve vs. original points using Plotly.
        :param grid_points: List or array of maturities for which the rate has been calculated.
        :param interpolated_rates: Interpolated rates computed by the spline.
        """
        go.Figure([
            go.Scatter(x=self.maturities, y=self.rates, mode='markers', name="Observed Rates"),
            go.Scatter(x=grid_points, y=interpolated_rates, mode='lines', name="Cubic Spline")
        ]).update_layout(
            title="Cubic Spline Interpolation of Zero-Coupon Rates (example)",
            xaxis_title="Maturity (in years)",
            yaxis_title="Annual Rate (decimal)"
        ).show()


class CurveBuilder:
    """
    Builds a QuantLib discount curve from zero-coupon instruments
    (or equivalents) and provides methods to compute discount factors and zero rates.
    """

    def __init__(self, calendar=None, day_count=None, business_convention=None):
        """
        :param calendar: Calendar (QuantLib Calendar), e.g. ql.UnitedStates().
        :param day_count: Day count convention (ql.DayCounter), e.g. ql.Actual365Fixed().
        :param business_convention: Business convention (ql.BusinessDayConvention),
                                    e.g. ql.Following or ql.ModifiedFollowing.
        """
        self.calendar = calendar if calendar else ql.UnitedStates(ql.UnitedStates.GovernmentBond)
        self.day_count = day_count if day_count else ql.Actual365Fixed()
        self.business_convention = business_convention if business_convention else ql.Following
        self.curve = None

        today = ql.Date().todaysDate() # set the evaluation date in QuantLib
        ql.Settings.instance().evaluationDate = today

    def build_curve(self, maturities, rates):
        """
        Builds a 'PiecewiseCubicZero' curve in QuantLib,
        by manually creating FixedRateBond-style helpers.

        :param maturities: List/array of maturities in years.
        :param rates:      List/array of zero-coupon rates in decimal,
                           in the same order as maturities.
        """
        instruments = []
        today = ql.Settings.instance().evaluationDate

        for mat, rate in zip(maturities, rates):
            tenor_in_days = int(mat * 365)
            maturity_date = today + tenor_in_days

            # Create a Schedule
            schedule = ql.MakeSchedule(
                effectiveDate=today,
                terminationDate=maturity_date,
                calendar=self.calendar,
                tenor=ql.Period(int(mat * 12), ql.Months),
                convention=self.business_convention
            )

            # Create a FixedRateBondHelper with coupon = rate
            bond_helper = ql.FixedRateBondHelper(
                ql.QuoteHandle(ql.SimpleQuote(100.0)),  # theoretical price
                1,                   # settlement days
                100.0,               # nominal
                schedule,
                [rate],              # list of coupons
                self.day_count,
                self.business_convention,
                100.0,               # redemption
                today
            )
            instruments.append(bond_helper)

        # Build the curve
        self.curve = ql.PiecewiseCubicZero(
            today,
            instruments,
            self.day_count
        )

    def get_discount_factor(self, T: float):
        """
        Returns the discount factor for a given maturity T.
        :param T: Maturity in years (float).
        :return: float discount factor
        """
        assert self.curve is not None, "The QuantLib curve is not yet built"

        today = ql.Settings.instance().evaluationDate
        date_target = today + int(T * 365)
        return self.curve.discount(date_target)

    def get_zero_rate(self, T: float, compounding=ql.Compounded, freq=ql.Annual):
        """
        Returns the zero rate for a given maturity T, based on a compounding
        method and frequency.
        :param T:   Maturity in years (float).
        :param compounding:  Compounding type (ql.Compounding).
        :param freq:         Frequency (ql.Frequency).
        :return: float, the zero rate in decimal.
        """
        assert self.curve is not None, "The QuantLib curve is not yet built"

        today = ql.Settings.instance().evaluationDate
        date_target = today + int(T * 365)
        zero_rate = self.curve.zeroRate(
            date_target, 
            self.day_count,
            compounding, 
            freq
        )
        return zero_rate.rate()


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


tickers = ["^IRX", "^FVX", "^TNX", "^TYX"]  # 3 mois, 5 ans, 10, 30
start_date = "2023-01-01"
end_date = "2023-03-01"

curve = CurveInterface(tickers, start_date, end_date)
for plot in [0.25, 1, 2, 5, 10, 20, 30]:
    discount_factor, zero_rate = curve.infer(plot)
    print(f"Maturity {plot:5.2f} yrs | DF = {discount_factor:6.4f} | ZeroRate cont. = {zero_rate * 100:4.2f}%")
