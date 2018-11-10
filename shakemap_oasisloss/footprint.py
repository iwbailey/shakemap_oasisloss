# Shakemap footprint
import numpy as np
import pandas as pd
from scipy.stats import norm
# import pdb


def assign_probtobin(x, intervals):
    """Assign 100% probability to one bin

    IN:
    x (float): value to assign
    intervals (pandas.IntervalIndex): list of bin intervals

    OUT:
    Numpy array of floats, same shape as intervals. Either all zeros or all
    zeros and one 1.0

    """

    # Initialize array of zero probabilities
    prob = np.zeros(np.shape(intervals))

    # Check if the value is within range, if so assign to the bin
    if(intervals.contains(x)):
        prob[intervals.get_loc(x)] = 1.0

    return prob


def calc_binprobs_norm(m0, s, intervals):
    """Calculate the discrete probabilties for each interval given the mean and std
    deviation of a normal distribution

    IN:
    m0 (float): mean
    s (float): std deviation
    intervals (pandas.IntervalIndex): bin intervals

    OUT:
    numpy array of probabilities

    """

    if s == 0:
        # Standard deviation = 0, just assign m0
        prob = assign_probtobin(m0, intervals)
    else:
        # CDF is Prob(X<=x)
        # ... so Prob(X<=x2) - Prob(X<=x1) gives Prob(x1 < X <= x2)
        # ? If we want Prob(x1 <= X < X2), it won't make a difference

        # TODO: We are calculating twice here. how much time would be saved if
        # just calculated once and checked that the bins touch each other.
        # if intervals.is_non_overlapping_monotonic:
        # prob
        prob2 = norm.cdf(intervals.right, m0, s)
        prob1 = norm.cdf(intervals.left, m0, s)
        prob = prob2 - prob1

    return prob


# ------------------------------------------------------------------------------


class ShakemapFootprint:
    # Constructor
    # IN:
    #  event_id
    #  Shakemap grid class with intensity measure & std dev defined
    #  Intensity measure to be used
    #  Intensity measure discretization (and min intensity)
    #  Spatial grid definition
    #  Number of sigma
    #  Event index

    def __init__(self, eventId, shakemap, areaPerilGrid, minIntens=6.0,
                 maxNsigma=4):
        """
        eventId: should be an integer for the event
        shakemap: a Shakemap grid using python class from shakemap_lookup
        intensIntervals: is pandas IntervalIndex defining the bins
            note the maximum interval should be inf

        """

        # Get the shakemap as a pandas data frame
        shakemap_df = pd.DataFrame.from_dict(shakemap.as_dict())

        # TODO: check if we need to correct median to mean in case of logPSA
        # intensities

        # Keep rows above the minimum
        isKeep = (shakemap_df['median'] +
                  maxNsigma*shakemap_df['std'] >= minIntens)

        shakemap_df = shakemap_df[isKeep]

        # TODO: Check case that we keep nothing

        # Assign grid to calculation grid
        shakemap_df['areaperil_id'] = areaPerilGrid.assign_gridid(
            shakemap_df['lon'], shakemap_df['lat'])

        # Create the data frame, using the fields we want
        self.df = shakemap_df.loc[:, ['areaperil_id', 'median', 'std']]
        self.df = self.df.reset_index()

        # change field name
        self.df.rename(columns={'median': 'mean'}, inplace=True)

        # Add the event id as 1st column
        self.df.insert(0, 'event_id', eventId)

        # Add weight for number of grid results here
        t = self.df.groupby('areaperil_id').size().reset_index()
        t.columns = ['areaperil_id', 'prob']
        t['prob'] = 1/t['prob']
        self.df = pd.merge(self.df, t, on='areaperil_id')

        return

    def as_oasistable(self, intensbins, minProb=1e-9):
        """Return the table as pandas table in oasis format

        IN:

        intensIntervals: (BinIntervals) class defining intensity intervals

        isUnc: (bool) True: consider uncertainty, default False

        OUTPUT: Pandas table with following fields:
        * event_id
        * areaperil_id
        * intensity_bin_index
        * prob

        """

        # Get an array of probabilities with each interval as separate column
        def myfun(x):
            """Need function to take a single argument"""
            return calc_binprobs_norm(x[0], x[1], intensbins.df.index)

        print('1')
        probs = np.apply_along_axis(myfun, axis=1,
                                    arr=self.df.loc[:, ['mean', 'std']].values)

        print('2')

        # Include the existing prob
        probs = self.df.prob.values[:, None]*probs

        # Convert to a data frame. We have to repeat the existing data frame
        # for each intensity bin.
        outdf = self.df.loc[:, ['event_id', 'areaperil_id']]
        outdf = pd.concat([outdf]*len(intensbins.df), ignore_index=True)
        outdf['intensity_bin_index'] = np.tile(intensbins.df.bin_id.values,
                                               len(self.df))
        outdf['prob'] = probs.flatten()

        # Get rid of low probability entries
        outdf = outdf[outdf.prob >= minProb]

        # Keep only needed for output
        return outdf.loc[:, ['event_id', 'areaperil_id', 'intensity_bin_index',
                             'prob']]
