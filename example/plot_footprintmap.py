"""Read in the footprint and plot the exceedance probability for a given
intensity.

"""

import pandas as pd
from matplotlib import pyplot as plt
from matplotlib import pylab
from oasis_utils import read_footprint, get_areaperilcoords, read_intensbins

# import pdb

# Parameters ------------------------------------------------------------------
eventId = 1

ifile_fp = "static/footprint.csv"
ifile_intensbins = "static/intensity_bin_dict.csv"
ifile_areaperil = "./areaperilgrid.yaml"

intensval = 5.5

pd.options.display.max_rows = 10

# Script ----------------------------------------------------------------------


def plot_footprintmap(locns, intensval):
    """ Plots a map of the locations, coloured by their loss
    """
    print("Generating plot...")
    fig, ax = plt.subplots(1, 1, facecolor='white')

    # Add the locations
    cax = ax.scatter(locns['lon'].values, locns['lat'].values,
                     c=locns['prob'].values, s=2.0,
                     marker='s',
                     edgecolors=None)

    # Formatting
    ax.set_aspect('equal')
    ax.autoscale(tight=True)
    ax.grid()

    # Add a color bar
    plt.colorbar(cax, orientation='vertical',
                 label='Exceedance Prob')

    plt.title("Prob of exceeding intensity %.2f" % intensval)

    return 1


# Read the footprint for the eventid we want

# Read the footprint
fp = read_footprint(ifile_fp, eventId)

# Read the lat lon for all areaperil_ids
areaperilxy = get_areaperilcoords(ifile_areaperil, fp.index.levels[0].values)

# Combine with bins
fp = pd.merge(fp, read_intensbins(ifile_intensbins), left_index=True,
              right_index=True)

# Sum the prob for the bin containing the intensity we want to plot and higher
# bins.
fp_plot = fp[fp.right >= intensval]['prob'].groupby(level=0).sum()

# Combine with the lat lon
fp_plot = pd.concat([areaperilxy, fp_plot], axis=1)

# Plot the map
plot_footprintmap(fp_plot, intensval)

# Show the plot
print('Pausing while plot is shown...')
pylab.show(block=True)
