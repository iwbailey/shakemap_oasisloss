

import numpy as np
import csv
from matplotlib import pyplot as plt
from matplotlib import pylab

from shakemap_lookup import FragilityCurve
from shakemap_lookup import USGSshakemapGrid

from damagefunction import DamageFunction
from footprint import ShakemapFootprint
from oasis_dicts import create_bindict

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

intensbins = np.arange(5.45, 10.15, 0.1)
mdrbins = np.arange(0.0, 1.01, 0.01)

vulnerability_id = 1
event_id = 1
interval_type = 1201  # Oasis code for interval type

# Output files
ofile_damdict = 'static/damage_bin_dict.csv'
ofile_intensdict = 'static/intensity_bin_dict.csv'
ofile_vuln = 'static/vulnerability.csv'
ofile_fp = 'static/footprint.csv'

# -----------------------------------------------------------------------------

#TODO set up the areaperil dict

# Set up the intensity bins

intensbindict = create_bindict(mdrbins, interval_type)

# Read in shakemap as a footprint table
fp = ShakemapFootprint(event_id, USGSshakemapGrid(ifileSM, 'MMI'), minIntens)

# Write to file with columns in right order
fp.df.to_csv(ofile_fp, columns=['event_id', 'areaperil_id',
                                'intensity_bin_index', 'prob'], index=False,
             quoting=csv.QUOTE_NONNUMERIC)
print("Written to %s" % ofile_fp)

# Read in fragility curve
frag = FragilityCurve(ifileFrag)

# Set up the shakemap footprint


# Set up the damage function
dmg = DamageFunction(vulnerability_id, frag, damageStateDict,
                     0.5*(intensbins[:-1] + intensbins[1:]), mdrbins)

# Set up the damage dict
damagebindict = create_bindict(mdrbins, interval_type)



# Convert to pandas array with oasis headers
oasisVuln = dmg.vulnarr_to_oasis()

# -----------------------------------------------------------------------------

oasisVuln.to_csv(ofile_vuln, columns=['vulnerability_id',
                                      'intensity_bin_index',
                                      'damage_bin_index', 'prob'], index=False,
                 quoting=csv.QUOTE_NONNUMERIC)
print("Written to %s" % ofile_vuln)

intensbindict.to_csv(ofile_intensdict, columns=['index', 'bin_from', 'bin_to',
                                                'interpolation',
                                                'interval_type'],
                     index=False, quoting=csv.QUOTE_NONNUMERIC)
print("Written to %s" % ofile_intensdict)

damagebindict.to_csv(ofile_damdict, columns=['index', 'bin_from', 'bin_to',
                                             'interpolation', 'interval_type'],
                     index=False, quoting=csv.QUOTE_NONNUMERIC)
print("Written to %s" % ofile_damdict)
