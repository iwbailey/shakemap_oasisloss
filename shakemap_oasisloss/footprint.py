# Shakemap footprint
import pandas as pd


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

    def assign_intensbins(self, intensIntervals):
        # TODO assign to intensity bins

        return

    # TODO: Function outputs to new csv file for ktools
    def as_oasistable(self, intensbins):
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

        out = self.df.loc[self.df['mean'] >= intensbins.min()]

        out = out.assign(
            intensity_bin_index=intensbins.df.loc[out['mean']].bin_id.values)

        # TODO: calculate prob within bins according to following
        # Calculate the cdf at each interval bound
        #
        # for each mean and std deviation, calculate the prob density of
        # each row
        #
        # Expand the table

        # Keep only needed for output
        out = out.loc[:, ['event_id', 'areaperil_id', 'intensity_bin_index',
                          'prob']]

        return out
    # TODO: Function appends to existing csv file for ktools
