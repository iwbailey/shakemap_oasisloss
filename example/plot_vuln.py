"""
Plot the damage function.

"""
from matplotlib import pyplot as plt
from matplotlib import pylab
import pandas as pd
import seaborn as sns

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
vuln0 = read_csvtodf(ifile_vuln)

# extract the vulnerability we're interested in
vuln0 = vuln0.loc[vuln0.vulnerability_id == vulnId]
vuln0.drop('vulnerability_id', 1, inplace=True)

# Set the index
vuln0 = vuln0.sort_values(['intensity_bin_id', 'damage_bin_id'], axis=0,
                          ascending=[True, True])
vuln0 = vuln0.set_index(['intensity_bin_id', 'damage_bin_id'])

# Calculate cumulative and exceedance prob
vuln1 = vuln0.groupby('intensity_bin_id').cumsum().rename(columns={'prob':
                                                                   'cprob'})

# prob of bin and exceding it, not prob of exceeding it
vuln2 = vuln0.iloc[::-1].groupby('intensity_bin_id').cumsum().rename(columns={
    'prob': 'exprob'})

# Combine with probabilities
vuln = pd.concat([vuln0, vuln1, vuln2], axis=1)

# Read the damage bins
dmg = read_csvtodf(ifile_dmgmap)
dmg.set_index('index', inplace=True)
dmg.index.names = ['damage_bin_id']

# Join
vuln = pd.merge(vuln.reset_index(), dmg[['bin_from', 'bin_to']],
                left_on="damage_bin_id",
                right_index=True)
vuln.rename(index=str, columns={'bin_to': 'UpperDamageRatio',
                                'bin_from': 'LowerDamageRatio'},
            inplace=True)
vuln = vuln.assign(DamageRatio=0.5*(vuln.LowerDamageRatio +
                                    vuln.UpperDamageRatio))

# Read the intensity bins

print("Generating plot...")
fig, ax = plt.subplots(1, 1, facecolor='white')

# Add the locations
pts = ax.scatter(vuln.intensity_bin_id, vuln.DamageRatio,
                 s=1+100*vuln.prob,
                 c=vuln.exprob, cmap="RdYlGn",
                 marker='o',
                 alpha=0.5, edgecolors=None)

cb = plt.colorbar(pts)
cb.set_label("Exceedance Probability")

# Formatting
ax.set_facecolor("lightgray")
ax.autoscale(tight=True)
ax.grid()
ax.set_xlabel('Intensity Bin ID')
ax.set_ylabel('Damage Ratio')

# Plot
fig2, ax2 = plt.subplots(figsize=(9, 6))
sns.heatmap(vuln.pivot('DamageRatio', 'intensity_bin_id', 'exprob'),
            ax=ax2, cmap='Spectral_r', vmin=0.0, vmax=1.0, center=0.5)

ax2.invert_yaxis()

# Show the plot
print('Pausing while plot is shown...')
pylab.show(block=True)
