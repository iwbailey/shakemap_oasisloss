# Test that the damage function is working

import sys
import numpy as np
import pandas as pd

from matplotlib import pyplot as plt
from matplotlib import pylab

from shakemap_lookup import FragilityCurve
from shakemap_oasisloss import DamageFunction
from shakemap_oasisloss import BinIntervals


# Parameters ----

# Input fragility
infrag = pd.DataFrame([
    [5.0, 0.076, 0.016, 0.005, 0.0, 0.0],
    [6.0, 0.489, 0.121, 0.031, 0.011, 0.0],
    [7.0, 0.739, 0.558, 0.263, 0.051, 0.005],
    [8.0, 0.908, 0.781, 0.548, 0.248, 0.051],
    [9.0, 0.989, 0.918, 0.791, 0.532, 0.381],
    [10.0, 0.995, 0.979, 0.928, 0.781, 0.659],
    [11.0, 1.0, 0.994, 0.989, 0.959, 0.949]],
                      columns=["MMI", "negligible", "moderate", "substantial",
                               "very_heavy", "destruction"])

# Map from input damage states to MDR exceeded
damageStateDict = {
    'negligible':  0.0,  # 0.0 means >0, not >=0
    'moderate':    0.1,
    'substantial': 0.25,
    'very_heavy':  0.5,
    'destruction': 1.0}

# Intensity bin edges
intensbinedges = np.linspace(5.0, 11.0, 61)

# damage ratio bin edges
drbinedges = np.linspace(0.0, 1.0, 101)

# Vulnerabilty id
vulnId = 1

# Limit pandas display size
pd.options.display.max_rows = 10

# Functions -----


def checkplot_interpolatedamage(frag, exprobcurves):
    """Read in fragility function and plot

    Plot the fragility curves as read in
    IN: Pandas data frame
          column 1 is named 'MMI'
          columns 2+ are named the damage states
    """

    fig, ax = plt.subplots(1, 1, facecolor='white')

    # Plot underlying fragility curve
    for c in frag.damagestates():
        ax.plot(frag.intensities, frag.exceedprob[c].values, label=c)
        ax.plot(exprobcurves.index.mid, exprobcurves[c].values, '--', label=c)
    ax.set_xlabel(frag.intensitymeasure)
    ax.set_ylabel('ProbExceedance')
    ax.grid(True)
    ax.legend(loc=2, frameon=False, framealpha=0.5)

    plt.title('Fragility curve')

    return


# Script -----

# Read in fragility curve
frag = FragilityCurve(infrag)

# Set up the damage bins
drbins = BinIntervals(drbinedges, closed="right")
print('\nDamage ratio bins:')
print(drbins.bin_id)

# Set up the intensity bins, display
intensbins = BinIntervals(intensbinedges, closed='left')
print('\nIntensity bins:')
print(intensbins.bin_id)

# Set up the damage function
dmg = DamageFunction(vulnId, frag, damageStateDict,
                     intensbins.intervals, drbins.intervals)

print('\nDamage prob matrix as data frame:')
print(dmg.prob)

# Test the indexing
testIntens = 5.278
print('\nDamage Ratio PDF for intensity=%.2f:' % testIntens)
print(dmg.prob.loc[testIntens])
print("Sum probs = %.2f" % dmg.prob.loc[testIntens].sum())

testDRbin = 2
print('\nProbability of damage in interval %s for intensity=%.2f:' %
      (dmg.prob.columns[testDRbin], testIntens))
print(dmg.prob.loc[testIntens].iloc[testDRbin])

# Convert to pandas array with oasis headers
oasisVuln = dmg.vulnarr_to_oasis(intensbins, drbins, minProb=1e-9)

# display to terminal
print('Footprint table:')
print(oasisVuln)

# Plot the input fragility function vs interpolated
checkplot_interpolatedamage(frag, dmg.exprobcurves)

# Plot as an array
fig, ax = plt.subplots(1, 1, facecolor='white')
cax = ax.imshow(dmg.prob.values.T, interpolation='none', origin='lower',
                aspect='auto',
                extent=(intensbinedges[0], intensbinedges[-1],
                        drbinedges[0], drbinedges[-1]))
plt.xlabel(frag.intensitymeasure)
plt.ylabel('Damage Ratio')
ax.grid()
plt.colorbar(cax, ax=ax, orientation='vertical',
             label="Probability")

# Plot exceedance prob as an array
exprob = np.cumsum(dmg.prob.values.T[::-1, :], axis=0)[::-1, :]
fig, ax = plt.subplots(1, 1, facecolor='white')
cax = ax.imshow(exprob, interpolation='none', origin='lower',
                aspect='auto',
                extent=(intensbinedges[0], intensbinedges[-1],
                        drbinedges[0], drbinedges[-1]),
                vmin=0, vmax=1)
plt.xlabel(frag.intensitymeasure)
plt.ylabel('Damage Ratio')
ax.grid()
plt.colorbar(cax, ax=ax, orientation='vertical',
             label="Exceedance Probability")


print('Pausing while plot is shown...')
pylab.show(block=True)


sys.exit()
