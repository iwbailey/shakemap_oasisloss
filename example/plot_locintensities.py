"""
Join the tables to get the intensity assignment for each location
"""

from matplotlib import pyplot as plt
from matplotlib import pylab
import pandas as pd

from oasis_utils import read_csvtodf, read_footprint, read_intensbins, \
    plot_footprintmap

# Parameters ------------------------------------------------------------------
eventId = 1

ifile_fp = "static/footprint.csv"
ifile_intensbins = "static/intensity_bin_dict.csv"
ifile_loc = "./input/locations_encoded.csv"

intensval = 5.5

pd.options.display.max_rows = 10

# Functions -------------------------------------------------------------------


def plot_lossmap(locns):
    """ Plots a map of the locations, coloured by their loss
    """
    print("Generating plot...")
    fig, ax = plt.subplots(1, 1, facecolor='white')

    # Add the locations
    cax = ax.scatter(locns['lon'].values, locns['lat'].values,
                     c=locns['meanLoss'].values, s=60.0,
                     marker='v',
                     edgecolors='k')

    # Formatting
    ax.set_aspect('equal')
    ax.autoscale(tight=True)
    ax.grid()

    # Add a color bar
    plt.colorbar(cax, orientation='vertical',
                 label='Loss')

    # Show the plot
    print('Pausing while plot is shown...')
    pylab.show(block=True)
    return 1


# Script ----------------------------------------------------------------------

# Read the footprint for the eventid we want
fp = read_footprint(ifile_fp, eventId)

# Read the intensity bins and join
fp = pd.merge(fp, read_intensbins(ifile_intensbins), left_index=True,
              right_index=True)

# Get the exceedance probability for the intensity we want
fp = fp[fp.right >= intensval]['prob'].groupby(level=0).sum()

# Read location file
locs = read_csvtodf(ifile_loc)
locs.set_index('coverage_id', drop=True, inplace=True)
locs.index.names = ['locid']

# Join the footprint by event id
locs = pd.merge(locs, fp.to_frame(), left_on='areaperil_id', right_index=True)

# Plot
plot_footprintmap(locs)
