# Create the static inputs for our file

import sys
import os
from csv import QUOTE_NONNUMERIC as CSVQUOTE
import numpy as np

from matplotlib import pyplot as plt
from matplotlib import pylab

from shakemap_lookup import FragilityCurve
from shakemap_lookup import USGSshakemapGrid

from shakemap_oasisloss import AreaPerilGrid
from shakemap_oasisloss import BinIntervals
from shakemap_oasisloss import ShakemapFootprint
from shakemap_oasisloss import DamageFunction

# -----------------------------------------------------------------------------
# Parameters

ifileSM = os.path.join(os.path.expanduser('~'), 'Downloads', 'usgs_shakemap',
                       'grid_70116556_v01.0.xml.zip')
ifileSMunc = os.path.join(os.path.expanduser('~'), 'Downloads', 'usgs_shakemap',
                          'uncertainty_70116556_v01.0.xml.zip')

ifileFrag = '/home/iwbailey/projects/shakemap_lookup/inputs/my_fragility.csv'

# Map from input damage states to MDR exceeded
damageStateDict = {
    'negligible':  0.0,  # 0.0 means >0, not >=0
    'moderate':    0.1,
    'substantial': 0.25,
    'very_heavy':  0.5,
    'destruction': 1.0}

intensBinEdges = np.arange(5.45, 10.15, 0.1)
intensBinEdges[-1] = np.inf

# Damage ratio bins
drBinEdges = np.linspace(0.0, 1.0, 101)
drBinEdges = np.insert(drBinEdges, 0, 0.0)

vulnerability_id = 1
event_id = 1
interval_type = 1201  # Oasis code for interval type

# Output files
ofile_damdict = 'static/damage_bin_dict.csv'
ofile_intensdict = 'static/intensity_bin_dict.csv'
ofile_vuln = 'static/vulnerability.csv'
ofile_fp = 'static/footprint.csv'

# -----------------------------------------------------------------------------

# Set up the damage bins ----
damagebins = BinIntervals(drBinEdges, 'right')

# Write the damage_bin_dict
damagebins.to_oasisdf().to_csv(ofile_damdict, index=False,
                               quoting=CSVQUOTE)
print("Written to %s" % ofile_damdict)

# Set up the intensity bins ----
intensbins = BinIntervals(intensBinEdges, closed='left')

# Write to file
intensbins.to_leftright().to_csv(ofile_intensdict, index=False,
                                 quoting=CSVQUOTE)
print("Written to %s" % ofile_intensdict)


# Read in the Shakemap ----
print("Reaing shakemap...")
myShakemap = USGSshakemapGrid(ifileSM, 'MMI', ifileSMunc, isQuiet=True)

# Set up the areaperil dict ----
areaperilMap = AreaPerilGrid(myShakemap.xlims(False), myShakemap.nx(),
                             myShakemap.ylims(False), myShakemap.ny())

# TODO: Write reference for the areaperil grid whatever's needed for geocoding

# Read in shakemap as a footprint table ----
print("Creating footprint..")
fp = ShakemapFootprint(event_id, myShakemap, areaperilMap, intensbins.min())

# Write to file with columns in right order
print("Calculating uncertainty bins...")
fp.as_oasistable(intensbins).to_csv(ofile_fp, index=False,
                                    quoting=CSVQUOTE)
print("Written to %s" % ofile_fp)

# Read in fragility curve ----
print("Reading fragility function from file...")
frag = FragilityCurve(ifileFrag)

# Set up the damage function ----
print("Setting up damage function")
dmg = DamageFunction(vulnerability_id, frag, damageStateDict,
                     intensbins.intervals, damagebins.intervals)

# Write to file
oasisVuln = dmg.vulnarr_to_oasis(intensbins,
                                 damagebins).to_csv(ofile_vuln, index=False,
                                                    quoting=CSVQUOTE)
print("Written to %s" % ofile_vuln)
