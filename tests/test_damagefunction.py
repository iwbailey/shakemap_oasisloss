

import numpy as np
import csv
import os
from matplotlib import pyplot as plt
from matplotlib import pylab

from shakemap_lookup import FragilityCurve
from shakemap_oasisloss import DamageFunction


# Parameters ----

# Input file
ifile = os.path.join('.', 'inputs', 'my_fragility.csv')

# Map from input damage states to MDR exceeded
damageStateDict = {
    'negligible':  0.0,  # 0.0 means >0, not >=0
    'moderate':    0.1,
    'substantial': 0.25,
    'very_heavy':  0.5,
    'destruction': 1.0}

# Intensity bin edges
intensbins = np.arange(5.45, 10.15, 0.1)

# damage ratio bin edges
drbins = np.arange(0.0, 1.01, 0.01)

# Vulnerabilty id
vulnId = 1

# Script -----

# Read in fragility curve
frag = FragilityCurve(ifile)

# Set up the damage function
dmg = DamageFunction(vulnId, frag, damageStateDict,
                     0.5*(intensbins[:-1] + intensbins[1:]), drbins)

# Plot
fig, ax = plt.subplots(1, 1, facecolor='white')
cax = ax.imshow(dmg.prob, interpolation='none', origin='lower',
                aspect='auto',
                extent=(intensbins[0], intensbins[-1],
                        drbins[0], drbins[-1]))
plt.xlabel(frag.intensitymeasure)
plt.ylabel('Damage Ratio')
ax.grid()
plt.colorbar(cax, ax=ax, orientation='vertical',
             label="Probability")

print('Pausing while plot is shown...')
pylab.show(block=True)

# Convert to pandas array with oasis headers
oasisVuln = dmg.vulnarr_to_oasis()

# display to terminal
print('Footprint table:')
print(oasisVuln.df)
