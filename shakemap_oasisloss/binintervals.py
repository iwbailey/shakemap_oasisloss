""" Definitions of bins in a table """
import pandas as pd
import numpy as np


class BinIntervals(object):
    def __init__(self, binedges, closed='left'):
        """Set bins. return as pandas Series
        """

        # TODO: only allow left or right closed
        # TODO check that oasis is by default closed
        bins = pd.IntervalIndex.from_breaks(binedges, closed=closed)

        # Check, self explanatory
        if bins.is_non_overlapping_monotonic is False:
            print("ERROR: bins are overlapping or not in order")

        # Number of bins, one less than number of edges
        nBins = len(bins)

        # Set up the data frame, containing only the ids
        self.bin_id = pd.Series(1 + np.arange(0, nBins), index=bins,
                                name='bin_id')
        return

    def get_intervals(self):
        return self.bin_id.index

    # Define intervals as a computed variable
    intervals = property(get_intervals)

    def to_breaks(self):
        """Return a numpy array of the bin edges"""
        return np.append(self.intervals.left.values, self.max())

    def check_damagebins(self):
        """Check that the damage ratios are okay if these are damage bins """
        # Check first interval starts with zero and last ends with 1
        EPS = 1e-12
        if abs(self.min()) > EPS:
            print("WARNING: first bin does not start at 0")

        # TODO: check greater than 1 might actually be okay in oasis
        if abs(self.max() - 1) > EPS:
            print("WARNING: last bin does not end at 1.0")

    def min(self):
        """Return the minimum value of the lowest bin"""
        return self.intervals.min().left

    def max(self):
        """Return the maximum value of the highest bin"""
        return self.intervals.max().right

    def isin(self, x):
        """From an array of values return True if within at least one bin"""
        myfun = np.vectorize(self.intervals.contains)
        return myfun(x)

    def to_leftright(self):
        """Return the left and right edges of the bins as columns"""
        outdf = self.bin_id.to_frame()
        outdf['left'] = self.intervals.left.values
        outdf['right'] = self.intervals.right.values
        outdf['closed'] = self.intervals.closed
        outdf = outdf.reset_index(drop=True)
        return outdf

    def to_oasisdf(self, isInterp=True, interval_type=1201):
        """Return the bin intervals as an df using the oasis dict column headers.

        """

        # Get the ids in first column and rename index as used by oasis
        outdf = self.bin_id.to_frame()
        outdf.columns = ['index']

        # Get the other fields from the index
        outdf['bin_from'] = outdf.index.left.values
        outdf['bin_to'] = outdf.index.right.values
        outdf['interpolation'] = outdf.index.mid.values
        outdf['interval_type'] = interval_type

        # When a bin edge is inf, the interpolation point is modified
        if np.isinf(self.max()):
            outdf['interpolation'][-1] = self.intervals.max().left

        return outdf
