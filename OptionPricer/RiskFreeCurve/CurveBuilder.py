import QuantLib as ql


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
