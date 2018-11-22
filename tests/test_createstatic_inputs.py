

import numpy as np
import csv
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

ifileSM = '/home/iwbailey/Downloads/usgs_shakemap/grid_1000dyad_v11.0.xml.zip'
ifileFrag = '/home/iwbailey/projects/shakemap_lookup/inputs/my_fragility.csv'

# Map from input damage states to MDR exceeded
damageStateDict = {
    'negligible':  0.0,  # 0.0 means >0, not >=0
    'moderate':    0.1,
    'substantial': 0.25,
    'very_heavy':  0.5,
    'destruction': 1.0}

intensBinEdges = np.arange(5.45, 10.15, 0.1)

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
                               quoting=csv.QUOTE_NONNUMERIC)
print("Written to %s" % ofile_damdict)

# Set up the intensity bins ----
intensbins = BinIntervals(intensBinEdges, closed='left')

# TODO: Write to file
intensbindict.to_csv(ofile_intensdict, columns=['index', 'bin_from', 'bin_to',
                                                'interpolation',
                                                'interval_type'],
                     index=False, quoting=csv.QUOTE_NONNUMERIC)
print("Written to %s" % ofile_intensdict)


# Read in the Shakemap ----
myShakemap = USGSshakemapGrid(ifileSM, 'MMI')

# Set up the areaperil dict ----
areaperilMap = AreaPerilGrid(myShakemap.xlims(False), myShakemap.nx(),
                             myShakemap.ylims(False), myShakemap.ny())

# TODO: Write whatever's needed for geocoding

# Read in shakemap as a footprint table ----
fp = ShakemapFootprint(event_id, myShakemap, areaperilMap, intensbins.min())

# Write to file with columns in right order
fp.df.to_csv(ofile_fp, columns=['event_id', 'areaperil_id',
                                'intensity_bin_index', 'prob'], index=False,
             quoting=csv.QUOTE_NONNUMERIC)
print("Written to %s" % ofile_fp)

# Read in fragility curve ----
frag = FragilityCurve(ifileFrag)

# Set up the damage function ----
dmg = DamageFunction(vulnerability_id, frag, damageStateDict,
                     0.5*(intensbins[:-1] + intensbins[1:]), mdrbins)

# TODO: Write to file
oasisVuln = dmg.vulnarr_to_oasis()
oasisVuln.to_csv(ofile_vuln, columns=['vulnerability_id',
                                      'intensity_bin_index',
                                      'damage_bin_index', 'prob'], index=False,
                 quoting=csv.QUOTE_NONNUMERIC)
print("Written to %s" % ofile_vuln)
