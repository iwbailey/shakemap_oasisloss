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
                     'grid_1000dyad_v11.0.xml.zip')
ifile_unc = os.path.join(os.path.expanduser('~'), 'Downloads', 'usgs_shakemap',
                     'uncertainty_1000dyad_v11.0.xml.zip')

# which intensity measure to use
intensMeasure = 'MMI'

# Define the intensity bin edges
binedges = np.linspace(5.45, 10.05, 47)
binedges[-1] = float("inf")  # open upper bin

# event id
eventId = 1


# Script -----

# load the shakemap into a class
sm = USGSshakemapGrid(ifile, intensMeasure)

# Define an area peril grid from the shakemap properties
geoGrid = AreaPerilGrid(sm.xlims(False), sm.nx(), sm.ylims(False), sm.ny())

# Define a footprint
fp = ShakemapFootprint(eventId, sm, geoGrid, binedges[0])

# display to terminal
print('\nFootprint table:')
print(fp.df.head(10))

# Set up the intensity bins, display
intensbins = BinIntervals(binedges, closed='left')
print('\nIntensity bins:')
print(intensbins.df)

# Get the table in oasis format with no std deviation
print("\nFootprint:")
print(fp.as_oasistable(intensbins).head(10))
