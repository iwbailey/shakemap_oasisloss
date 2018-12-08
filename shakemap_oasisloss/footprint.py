# Shakemap footprint
import numpy as np
import pandas as pd
from scipy.stats import norm

# import pdb

# ------------------------------------------------------------------------------


class ShakemapFootprint:
    # Class for a USGS shakemap grid footprint stored as a pandas dataframe
    #
    # Each grid point is stored as a row with the mean and std deviation of the
    # intensity measure used.
    #
    # IN:
    #  event_id
    #  Shakemap grid class with intensity measure & std dev defined
    #  AreaPerilGrid class
    #  Minimum intensity
    #  minimum probability
    #
    # PROPERTIES:
    #  df is a dataframe with following columns
    #    event_id: id for the specific footprint
    #    areaperil_id: areaperil at which each point is defined
    #    m0: Mean intensity
    #    sd: std deviation of the intensity
    #    prob: Discrete probability of this m0/sd combination
    #
    # If multiple shakemap grid points get assigned to the areaperil, the prob
    # is divided among the areaperil entries

    def __init__(self, eventId, shakemap, areaPerilMap, minIntens=6.0,
                 minProb=1e-6):
        """
        eventId: should be an integer for the event
        shakemap: a Shakemap grid using python class from shakemap_lookup
        intensIntervals: is pandas IntervalIndex defining the bins
            note the maximum interval should be inf

        """

        # Get the shakemap as a pandas data frame
        df = pd.DataFrame.from_dict(shakemap.as_dict())

        # Change field name to avoid conflicts with functions
        df = df.loc[:, ['lat', 'lon', 'm0', 'sd']]

        # Assign grid to areperils
        df = df.assign(areaperil_id=areaPerilMap.assign_xytoid(
            df['lon'], df['lat']))
        df = df.drop(['lat', 'lon'], 1)

        # Assign prob to each areaperil based on number of grid points assigned
        t = df.groupby('areaperil_id').size().reset_index()
        t.columns = ['areaperil_id', 'prob']
        t['prob'] = 1/t['prob']
        df = pd.merge(df, t, on='areaperil_id')

        # TODO: check if we need to correct median to mean in case of logPSA
        # intensities

        # Keep rows only when non-zero prob of intensity above the min
        # threshold.
        maxNsigma = norm.ppf(1-minProb, 0, 1)
        df = df[df.m0 + maxNsigma*df.sd >= minIntens]

        # Add the event id as 1st column
        df.insert(0, 'event_id', eventId)
        df = df.reset_index(drop=True)

        self.df = df.loc[:, ['event_id', 'areaperil_id', 'm0', 'sd', 'prob']]

        return

    def as_oasistable(self, bins, minProb=1e-9):
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

        # We have to repeat the existing data frame for each intensity
        # bin. Note concat stacks the same data frame
        outdf = self.df.copy(deep=True)

        if np.all(abs(outdf.sd < 1e-15)):
            # Case where all std deviations are zero. We look up the
            # appropriate interval for the mean.
            intervals = bins.intervals

            # Filter out where mean is out of bounds
            inbounds = np.vectorize(intervals.contains)
            outdf = outdf.loc[inbounds(outdf.m0.values), :]

            # Assign the rest
            outdf = outdf.assign(bin_id=bins.bin_id[outdf.m0].values)

        elif np.all(abs(outdf.sd >= 1e-15)):
            # Merge all combinations of the footprint and bin intervals using a
            # common key, then drop the key
            outdf = pd.merge(outdf.assign(key=0),
                             bins.to_leftright().assign(key=0),
                             on='key', how='outer').drop('key', 1)

            # Remove bins we know will be zero prob
            maxNsigma = norm.ppf(1-minProb, 0, 1)

            isKeep = ((outdf.left - outdf.m0 < maxNsigma*outdf.sd) &
                      (outdf.m0 - outdf.right <= maxNsigma*outdf.sd))
            outdf = outdf[isKeep]

            # Calculate the probabilties and combine with existing
            # probabilities
            outdf['prob'] = outdf.prob * (norm.cdf(outdf.right, outdf.m0,
                                                   outdf.sd) -
                                          norm.cdf(outdf.left, outdf.m0,
                                                   outdf.sd))

            # TODO: check that the prob adds up to 1 for all areaperil_ids??

        else:
            raise ValueError("Mixtures of zero and non-zero std dev")

        # Merge the results when there've been multiple prob distributions per
        # areaperilgrid
        outdf = outdf.groupby(by=['event_id', 'areaperil_id', 'bin_id'],
                              as_index=False)['prob'].sum()

        # Get the correct column name
        outdf.rename(columns={'bin_id': 'intensity_bin_index'}, inplace=True)

        return outdf.loc[:, ['event_id', 'areaperil_id', 'intensity_bin_index',
                             'prob']]
