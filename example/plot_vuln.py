"""
Plot the damage function.

"""
from matplotlib import pyplot as plt
from matplotlib import pylab
import pandas as pd

from oasis_utils import read_csvtodf

# Parameters ------------------------------------------------------------------
vulnId = 1
summaryset_id = 1

# loss per location
ifile_vuln = "static/vulnerability.csv"
ifile_dmgmap = "static/damage_bin_dict.csv"

pd.options.display.max_rows = 10

# Script ----------------------------------------------------------------------

# Read the location losses from the ELT file
vuln = read_csvtodf(ifile_vuln)
vuln = vuln.loc[vuln.vulnerability_id == vulnId]
vuln.drop('vulnerability_id', 1, inplace=True)

# Read the damage bins
dmg = read_csvtodf(ifile_dmgmap)
dmg.set_index('index', inplace=True)

vuln = vuln.merge(dmg['interpolation'].to_frame(), left_on='damage_bin_id',
                  right_on="index")
vuln.rename(index=str, columns={'interpolation': 'damageRatio'}, inplace=True)

print("Generating plot...")
fig, ax = plt.subplots(1, 1, facecolor='white')

# Add the locations
ax.scatter(vuln.intensity_bin_id, vuln.damageRatio,
           s=1000*vuln.prob,
           marker='o',
           alpha=0.2, edgecolors=None)

# Formatting
ax.autoscale(tight=True)
ax.grid()
ax.set_xlabel('Intensity Bin ID')
ax.set_ylabel('Damage Ratio')
# Show the plot
print('Pausing while plot is shown...')
pylab.show(block=True)
