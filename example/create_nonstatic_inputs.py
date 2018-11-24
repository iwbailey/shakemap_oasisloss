# Create all of the input files that are not static for the oasis loss
# calculation.
#
# Files are:
# * items.csv: defines groups of coverages
# * coverages.csv: defines the value of each thing that is covered

# Dependencies ----------------------------------------------------------------

import yaml
import sys
import numpy as np
import pandas as pd
from csv import QUOTE_NONNUMERIC as CSVQUOTE

from shakemap_oasisloss import AreaPerilGrid

# Parameters ------------------------------------------------------------------
ifile_loc = "./inputs/Hawaii_Mile_Markers_v2.csv"
ifile_areaperil = "./areaperilgrid.yaml"
vulnId = 1

ofile_items = 'input/items.csv'
ofile_cvg = 'input/coverages.csv'

# Functions -------------------------------------------------------------------


def locns2cvgs(locns):
    """Get one coverage per location based on its TIV

    Use the location id as coverage id and tiv as the tiv

    """
    coverages = pd.DataFrame.from_dict({
        'coverage_id': locns['id'].values,
        'tiv': locns['tiv'].values
    })
    return coverages


def locns2items(locns):
    """Get one item per location

    item_id and coverage_id are the same

    """
    items = pd.DataFrame.from_items((
        ('item_id', locns['id'].values),
        ('coverage_id', locns['id'].values),
        ('areaperil_id', locns['areaperil_id']),
        ('vulnerability_id', locns['vulnerability_id']),
        ('group_id', locns['id'].values)  # this defines 100% correlation
    ))

    return items


# Script ----------------------------------------------------------------------

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
locns = locns[areaperilids.mask == 1]
print("%i locations left" % len(locns))

# Assign all the same vulnerability id
locns['vunerability_id'] = 1

# Get one coverage per location
coverages = locns2cvgs(locns)

# Write to file
coverages.to_csv(ofile_cvg, index=False, quoting=CSVQUOTE)
print("Written to %s" % ofile_cvg)

# Write items to files
items = locns2cvgs(locns)
items.to_csv(ofile_items, index=False, quoting=CSVQUOTE)
print("Written to %s" % ofile_items)
