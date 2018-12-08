"""For all locations compare the analytical mean loss with the sample mean loss """

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from matplotlib import pylab

from oasis_utils import read_csvtodf, read_locationlosses

# Parameters ------------------------------------------------------------------
ifile_elt = "./results/loclosses.csv"

pd.options.display.max_rows = 10

# Script ----------------------------------------------------------------------


def plot_lossloss(locns0):
    """ Plots a map of the locations, coloured by their loss
    """

    # Divide up the locations with a loss and those without
    locns = locns0[(locns0.meanLoss0 > 0.0) | (locns0.meanLoss > 0.0)]

    print("Generating plot...")
    fig, ax = plt.subplots(1, 1, facecolor='white')

    # Add the locations
    ax.errorbar(locns.meanLoss0, locns.meanLoss, yerr=0.5*locns.stddevLoss,
                fmt='ok', ecolor='k', elinewidth=1, markersize=3, capsize=2)

    maxloss = np.ceil((locns.meanLoss + 0.5*locns.stddevLoss).max())

    # TODO: add 1:1 line
    ax.plot([0, maxloss], [0, maxloss], '--r')

    # Formatting
    ax.set_aspect('equal')
    ax.set_xlim([0, maxloss])
    ax.set_ylim([0, maxloss])

    # ax.autoscale(tight=True)
    ax.grid()
    ax.set_xlabel("Analytical Mean Loss")
    ax.set_ylabel("Mean Sample Loss")

    return


# Read the location losses from the ELT file
loclosses = read_locationlosses(ifile_elt)

# Plot comparison of two means
plot_lossloss(loclosses)

# Show the plot
print('Pausing while plot is shown...')
pylab.show(block=True)
