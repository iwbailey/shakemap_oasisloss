# Create all of the input files that are not static for the oasis loss
# calculation.
#
# Files are:
# * items.csv: defines groups of coverages
# * coverages.csv: defines the value of each thing that is covered

# Dependencies ----------------------------------------------------------------
import pandas as pd
from csv import QUOTE_NONNUMERIC as CSVQUOTE

from shakemap_oasisloss import AreaPerilGrid

# Parameters ------------------------------------------------------------------
ifile_loc = "./inputs/Hawaii_Mile_Markers_v2.csv"
ifile_areaperil = ""
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
print "\t...%i rows" % len(locns)

# TODO: Assign locations to the areaperil

# TODO: Get rid of items not assigned

# Get one coverage per location
coverages = locns2cvgs(locns)

# Write to file
coverages.to_csv(ofile_cvg, index=False, quoting=CSVQUOTE)
print("Written to %s" % ofile_cvg)

# Assign all the same vulnerability id
locns['vunerability_id'] = 1

# Write items to files
items = locns2cvgs(locns)
items.to_csv(ofile_items, index=False, quoting=CSVQUOTE)
