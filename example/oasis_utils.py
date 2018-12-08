"""Module for utility functions around reading and plotting oasis inputs and
outputs

"""
import pandas as pd
import yaml
import sys

from shakemap_oasisloss import AreaPerilGrid


def read_csvtodf(ifile):
    """ Read a csv file into a dataframe and report the number of rows
    """
    print("Reading %s..." % ifile)
    df = pd.read_csv(ifile)
    print("\t...%i rows" % len(df))
    return df


def read_summarylosses(ifile_summ):
    """Read the summary loss file into a pandas array, extract the analytical mean
    loss from the first row, then get the sample losses in a dataframe. Return
    separately.

    meanloss, losssamples = read_summarylosses(ifile_csv)

    """

    # Read the summary file and set the index based on sidx
    summ = read_csvtodf(ifile_summ)
    summ.set_index('sidx', inplace=True)

    # Extract the mean from the first entry
    meanloss = summ.loss.loc[-1]  # Sum of analytic mean loss?
    losssamples = summ.loss[1:]

    return meanloss, losssamples


def read_footprint(ifile, event_id=1):
    """Read a single event from the footprint file and convert to a pandas series

    """

    # Read the file
    df = read_csvtodf(ifile)

    # Keep the footprint for the eventid we want
    df = df[df.event_id == event_id]
    df.drop('event_id', 1, inplace=True)

    # Convert to a data series with areaperil and intensity_bin_index as index
    prob = df.set_index(['areaperil_id', 'intensity_bin_index'])

    return prob


def read_intensbins(ifile):
    df = read_csvtodf(ifile)
    df.set_index('bin_id', inplace=True)
    df.index.names = ['intensity_bin_index']
    return df


def read_coverages(ifile):
    """Read the coverages file, using coverage_id as the index"""
    df = read_csvtodf(ifile)
    df.set_index('coverage_id', inplace=True)
    return df


def read_items(ifile):
    """Read the items file, using item_id as the index"""
    df = read_csvtodf(ifile)
    df.set_index('item_id', inplace=True)
    return df


def read_areaperilgrid(ifile):

    print("Reading %s..." % ifile)
    with open(ifile, 'r') as stream:
        try:
            # Expect the yaml file to contain fields that go into a dict
            gridparams = yaml.load(stream)
        except yaml.YAMLError as exc:
            print(exc)
            sys.exit()

    areaperilMap = AreaPerilGrid((gridparams['minlon'], gridparams['maxlon']),
                                 gridparams['nlon'],
                                 (gridparams['minlat'], gridparams['maxlat']),
                                 gridparams['nlat'])

    return areaperilMap


def get_areaperilcoords(ifile, areaperilids):
    # Read the areaperil map
    areaperilMap = read_areaperilgrid(ifile)

    lons, lats = areaperilMap.idtoxy(areaperilids)

    ap_lonlat = pd.DataFrame.from_dict({
        'lon': lons, 'lat': lats, 'areaperil_id': areaperilids})
    ap_lonlat.set_index('areaperil_id', inplace=True)

    return ap_lonlat


def read_locationlosses(ifile_elt, event_id=1):
    """Read the location loss file(elt) into a pandas dataframe"""
    elt = read_csvtodf(ifile_elt)
    elt = elt.loc[elt.event_id == event_id]
    elt.set_index(['summary_id', 'type'], inplace=True)

    # Type 1 is analytical mean
    loclosses = elt.loc[pd.IndexSlice[:, 1], 'mean']
    loclosses.index = loclosses.index.droplevel(1)
    loclosses.name = 'meanLoss0'

    # Type 2 is the sample mean
    loclossesSamp = elt.loc[pd.IndexSlice[:, 2],
                            ['mean', 'standard_deviation']]
    loclossesSamp.index = loclossesSamp.index.droplevel(1)
    loclossesSamp.columns = ['meanLoss', 'stddevLoss']

    # Join together
    loclosses = pd.merge(loclosses.to_frame(), loclossesSamp, left_index=True,
                         right_index=True)

    return loclosses
