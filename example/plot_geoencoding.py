"""
Check what the geoencoding looks like.

"""

# Dependencies ----------------------------------------------------------------

import yaml
import sys
import pandas as pd
from matplotlib import pyplot as plt
from matplotlib import pylab

from shakemap_oasisloss import AreaPerilGrid
from oasis_utils import get_areaperilcoords


# Parameters ------------------------------------------------------------------
ifile_loc = "./example_data/Hawaii_Mile_Markers_v2.csv"
ifile_areaperil = "./areaperilgrid.yaml"

pd.options.display.max_rows = 10


# Functions -------------------------------------------------------------------

# Read the input locations -----
print("Reading %s..." % ifile_loc)
locns = pd.read_csv(ifile_loc)
print("\t...%i rows" % len(locns))

# Set up the areaperil grid
with open(ifile_areaperil, 'r') as stream:
    try:
        # Expect the yaml file to contain fields that go into a dict
        gridparams = yaml.load(stream)
    except yaml.YAMLError as exc:
        print(exc)
        sys.exit()

areaperilMap = AreaPerilGrid((gridparams['minlon'], gridparams['maxlon']),
                             gridparams['nlon'],
                             (gridparams['minlat'], gridparams['maxlat']),
                             gridparams['nlat'])

# Assign locations to the areaperil
areaperilids = areaperilMap.assign_xytoid(locns.lon, locns.lat)

locns = locns.assign(areaperil_id=areaperilids.data)

# Remove locations that were not within grid
print("Removing %i locations not geoencoded to the grid space" %
      sum(1-areaperilids.mask))
locns = locns[areaperilids.mask == 0]
print("%i locations left" % len(locns))

# Read the lat lon for all areaperil_ids
areaperilxy = get_areaperilcoords(ifile_areaperil, locns.areaperil_id)


# Plot the locations
fig, axs = plt.subplots(1, 2, facecolor='white')
axs[0].plot(locns['lon'].values, areaperilxy['lon'], 'bo')
axs[0].set_xlabel('Location Lon')
axs[0].set_ylabel('AreaPeril Lon')

axs[1].plot(locns['lat'].values, areaperilxy['lat'], 'bo')
axs[1].set_xlabel('Location Lat')
axs[1].set_ylabel('AreaPeril Lat')

# Formatting
for ax in axs:
    ax.set_aspect('equal')
    ax.autoscale(tight=True)
    ax.grid()

# Show the plot
print('Pausing while plot is shown...')
pylab.show(block=True)
