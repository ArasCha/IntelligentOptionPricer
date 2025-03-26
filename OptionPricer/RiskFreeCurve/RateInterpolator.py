from scipy.interpolate import interp1d
import plotly.graph_objects as go


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
