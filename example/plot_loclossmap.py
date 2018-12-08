"""
Read in the outputs, plot ...
 - a map of the expected loss per location
"""

import pandas as pd
from matplotlib import pyplot as plt
from matplotlib import pylab

from oasis_utils import read_csvtodf, read_locationlosses

# Parameters ------------------------------------------------------------------
ifile_loc = "./input/locations_encoded.csv"
ifile_summ = "./input/gulsummaryxref.csv"
ifile_elt = "./results/loclosses.csv"

summsetId = 1

pd.options.display.max_rows = 10

# Script ----------------------------------------------------------------------


def plot_lossmap(locns, losstype='meanLoss0', includeZeros=False):
    """ Plots a map of the locations, coloured by their loss
    """

    # Divide up the locations with a loss and those without
    losslocns = locns[locns.meanLoss0 > 0.0]
    others = locns[locns.meanLoss0 == 0]

    print("Generating plot...")
    fig, ax = plt.subplots(1, 1, facecolor='white')

    # Add the locations
    cax = ax.scatter(losslocns['lon'].values, losslocns['lat'].values,
                     c=losslocns[losstype].values, s=losslocns['tiv'],
                     marker='v', alpha=0.8,
                     edgecolors=None)

    if includeZeros:
        ax.scatter(others.lon, others.lat, s=others['tiv'],
                   marker='o', edgecolors=[0.5, 0.5, 0.5], facecolors='none',
                   linewidths=0.5)

    # Formatting
    ax.set_aspect('equal')
    ax.autoscale(tight=True)
    ax.grid()

    # Add a color bar
    plt.colorbar(cax, orientation='vertical',
                 label='Loss')

    # Add a title
    plt.title("Expected GU loss by location, Type=%s" % losstype)

    return 1


# Read location file
locs = read_csvtodf(ifile_loc)

# Read the location losses from the ELT file
loclosses0 = read_locationlosses(ifile_elt)

# Read the summary file to get the coverageid
summ = read_csvtodf(ifile_summ)

# Keep the location level losses
summ = summ.loc[summ.summaryset_id == summsetId]

# Get the coverage id per loss
loclosses = pd.merge(loclosses0, summ, left_index=True, right_on='summary_id')

# Get the location detail per loss
loclosses = pd.merge(loclosses, locs, left_on="coverage_id",
                     right_on="coverage_id")

# Plot
plot_lossmap(loclosses)

# Show the plot
print('Pausing while plot is shown...')
pylab.show(block=True)
