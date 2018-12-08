"""Join the tables to get the intensity assignment for each location and
compare it to the damage ratio.

"""

from matplotlib import pyplot as plt
from matplotlib import pylab
import pandas as pd

from oasis_utils import read_csvtodf
from oasis_utils import read_locationlosses
from oasis_utils import read_items
from oasis_utils import read_coverages

from oasis_utils import read_footprint

# Parameters ------------------------------------------------------------------
eventId = 1
summaryset_id = 1
# loss per location
ifile_elt_perloc = "results/loclosses.csv"

# Need to tie summary id to coverage
ifile_summary = "input/gulsummaryxref.csv"
ifile_cvg = "input/coverages.csv"

# Need to get the TIV per coverage
ifile_item = "input/items.csv"

# Need the footprint to get the intensity per location
ifile_fp = "static/footprint.csv"

ifile_intensbins = "static/intensity_bin_dict.csv"

pd.options.display.max_rows = 10

# Script ----------------------------------------------------------------------

# Read the location losses from the ELT file
loclosses = read_locationlosses(ifile_elt_perloc)

# Read the summary file to get the coverageid
summ = read_csvtodf(ifile_summary)
summ = summ.loc[summ.summaryset_id == summaryset_id]
summ.drop('summaryset_id', 1, inplace=True)

# Get the coverage id per loss
loclosses = pd.merge(loclosses, summ, left_index=True, right_on='summary_id')

# Join with the items so we can get the areaperil
loclosses = pd.merge(loclosses, read_items(ifile_item), on="coverage_id")

# Join with the coverages so we can get the TIV
loclosses = pd.merge(loclosses, read_coverages(ifile_cvg),
                     left_on="coverage_id", right_index=True)

# Read the footprint for the eventid we want
fp = read_footprint(ifile_fp, eventId).reset_index()

loclosses = pd.merge(loclosses, fp, on='areaperil_id')

print("Generating plot...")
fig, axs = plt.subplots(2, 1, facecolor='white')

# Add the locations
axs[0].scatter(loclosses.intensity_bin_index, loclosses.meanLoss,
               s=1000*loclosses.prob,
               marker='o',
               alpha=0.1, edgecolors=None)
axs[0].set_ylabel('Sample Mean Loss')

axs[1].scatter(loclosses.intensity_bin_index, loclosses.meanLoss0,
               s=1000*loclosses.prob,
               marker='o',
               alpha=0.1, edgecolors=None)
axs[1].set_ylabel('Analytical Mean Loss')
axs[2].set_xlabel('Intensity Bin Index')

# Formatting
for ax in axs:
    ax.autoscale(tight=True)
    ax.grid()

# Show the plot
print('Pausing while plot is shown...')
pylab.show(block=True)
