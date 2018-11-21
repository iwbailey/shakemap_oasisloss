"""Test we can read in a shakemap and create an oasis footprint from it
"""

# Dependencies ----
import os
import numpy as np
import pandas as pd

from shakemap_lookup import USGSshakemapGrid
from shakemap_oasisloss import ShakemapFootprint
from shakemap_oasisloss import AreaPerilGrid
from shakemap_oasisloss import BinIntervals

# Parameters ----

# shakemap grid file
ifile = os.path.join(os.path.expanduser('~'), 'Downloads', 'usgs_shakemap',
                     'grid_70116556_v01.0.xml.zip')
ifile_unc = os.path.join(os.path.expanduser('~'), 'Downloads', 'usgs_shakemap',
                         'uncertainty_70116556_v01.0.xml.zip')

# which intensity measure to use
intensMeasure = 'MMI'

# Define the intensity bin edges
binedges = np.linspace(5.45, 10.05, 47)
binedges[-1] = float("inf")  # open upper bin

# event id
eventId = 1

pd.options.display.max_rows = 10

# Script -----

# load the shakemap into a class
sm = USGSshakemapGrid(ifile, intensMeasure)
# sm = USGSshakemapGrid(ifile, intensMeasure, ifile_unc)
print("%i grid points in shakemap" % sm.grid.size)

# Define an area peril grid from the shakemap properties
geoGrid = AreaPerilGrid(sm.xlims(False), sm.nx(), sm.ylims(False), sm.ny())

# Define a footprint
fp = ShakemapFootprint(eventId, sm, geoGrid, binedges[0])
print("%i grid points retained in footprint" % len(fp.df))

# Set up the intensity bins, display
intensbins = BinIntervals(binedges, closed='left')

# display to terminal
print('\nFootprint table:')
print(fp.df)

print('\nIntensity bins:')
print(intensbins.bin_id)

# Get the table in oasis format
print("\nFootprint:")
print(fp.as_oasistable(intensbins).head(20))
