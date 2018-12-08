"""
Read in the outputs, plot ...
 - a histogram of the event loss samples

"""

from matplotlib import pyplot as plt
from matplotlib import pylab

from oasis_utils import read_summarylosses

# Parameters ------------------------------------------------------------------
ifile_summ = "./results/eventloss_summary.csv"

# Functions -------------------------------------------------------------------


def plot_evlossdistr(lossSamples, meanloss):
    """Plot historgram of the loss summary"""

    ax = lossSamples.hist(cumulative=True, bins=len(lossSamples))
    ax.vlines(lossSamples.median(), ymin=0, ymax=100, label="Sample Median")
    ax.vlines(lossSamples.mean(), linestyles='dashed', ymin=0, ymax=100,
              label="Sample Mean")
    ax.vlines(meanloss, ymin=0, linestyles="dotted", ymax=100,
              label="Analytical Mean")
    plt.xlabel('Event Loss')
    plt.ylabel('Cumulative % of loss samples')
    plt.legend()

    print('Pausing while plot is shown...')
    pylab.show(block=True)
    return 1


# Script ----------------------------------------------------------------------

# Read the event loss estimate samples from the summary file
meanloss, losssamples = read_summarylosses(ifile_summ)

print("Analytical mean: %.1f" % meanloss)
print("Sample mean: %.1f" % losssamples.mean())

plot_evlossdistr(losssamples, meanloss)
