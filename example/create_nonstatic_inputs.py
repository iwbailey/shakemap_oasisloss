# Create all of the input files that are not static for the oasis loss
# calculation.
#
# Files are:
# * items.csv: defines groups of coverages
# * coverages.csv: defines the value of each thing that is covered

# Dependencies ----------------------------------------------------------------

import yaml
import sys
import pandas as pd
from csv import QUOTE_NONNUMERIC as CSVQUOTE

from shakemap_oasisloss import AreaPerilGrid

# Parameters ------------------------------------------------------------------
ifile_loc = "./example_data/Hawaii_Mile_Markers_v2.csv"
# ifile_loc = "./example_data/Hawaii_Mile_Markers_top15.csv"
ifile_areaperil = "./areaperilgrid.yaml"
vulnId = 1

ofile_items = 'input/items.csv'
ofile_cvg = 'input/coverages.csv'
ofile_gulsumm = 'input/gulsummaryxref.csv'
ofile_events = 'input/events.csv'

ofile_locns = 'input/locations_encoded.csv'


# Functions -------------------------------------------------------------------


def locns2cvgs(locns):
    """Get one coverage per location based on its TIV

    Use the location id as coverage id and tiv as the tiv

    """
    coverages = pd.DataFrame.from_dict({
        'coverage_id': locns['coverage_id'].values,
        'tiv': locns['tiv'].values
    })
    return coverages[['coverage_id', 'tiv']]


def locns2items(locns):
    """Get one item per location

    item_id and coverage_id are the same

    """
    items = pd.DataFrame.from_dict({
        'item_id': locns['coverage_id'].values,
        'coverage_id': locns['coverage_id'].values,
        'areaperil_id': locns['areaperil_id'].values,
        'vulnerability_id': locns['vunerability_id'].values,
        'group_id': locns['id'].values  # this defines 100% correlation
    })

    # Make sure the order is correct
    return items[['item_id', 'coverage_id', 'areaperil_id', 'vulnerability_id',
                  'group_id']]


def locns2gulsummary(locns):
    """Get one summary result per location

    summaryset_id is the reporting level
    """
    gulsummary1 = pd.DataFrame.from_dict({
        'coverage_id': locns['coverage_id'].values,
        'summary_id': locns['coverage_id'].values
    }).assign(summaryset_id=1)

    gulsummary2 = pd.DataFrame.from_dict({
        'coverage_id': locns['coverage_id'].values,
        'summary_id': 1,
    }).assign(summaryset_id=2)

    gulsum = pd.concat([gulsummary1, gulsummary2], ignore_index=False)
    return gulsum[['coverage_id', 'summary_id', 'summaryset_id']]


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
if areaperilids.mask.any():
    print("Removing %i locations not geoencoded to the grid space" %
          sum(areaperilids.mask))
    locns = locns[areaperilids.mask == 0]
    print("%i locations left" % len(locns))

# Coverage and item IDs need to start at 1
locns.reset_index(drop=True, inplace=True)
locns = locns.assign(coverage_id=locns.index+1)

# Assign all the same vulnerability id
locns['vunerability_id'] = 1

# Get one coverage per location
coverages = locns2cvgs(locns)

# Write to file
coverages.to_csv(ofile_cvg, index=False, quoting=CSVQUOTE)
print("Written to %s" % ofile_cvg)

# Write items to files
items = locns2items(locns)
items.to_csv(ofile_items, index=False, quoting=CSVQUOTE)
print("Written to %s" % ofile_items)

# Write location details to flie
locns.to_csv(ofile_locns, index=False, quoting=CSVQUOTE)
print("Written to %s" % ofile_locns)

# Write gulsummary to file
gulsummary = locns2gulsummary(locns)
gulsummary.to_csv(ofile_gulsumm, index=False, quoting=CSVQUOTE)
print("Written to %s" % ofile_gulsumm)

# Write list of events to file
events = pd.DataFrame([1], columns=['event_id'])
events.to_csv(ofile_events, index=False, quoting=CSVQUOTE)
print("Written to %s" % ofile_events)
