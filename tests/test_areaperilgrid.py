# Some tests on setting up a set of areaperilids that are defined by a regular
# spaced grid

# Dependencies
from collections import OrderedDict
import numpy as np
import pandas as pd

from shakemap_oasisloss import AreaPerilGrid

# Define the area peril grid we want to test
a = AreaPerilGrid((-180.0, 180), 360, (-80, 80), 160)


# Functionsn

def test_functions(x, y):
    """Test the class methods for input coordinates.Print the input coordinates and
    assignment.

    """

    print("\n")
    print("IN:")
    print(x)
    print(y)
    ix = a.assign_xcoords(x)
    iy = a.assign_ycoords(y)
    idx = a.assign_gridid(x, y)
    if not np.isscalar(x):
        print(pd.DataFrame.from_dict(OrderedDict([
            ('x', x),
            ('y', y),
            ('ix', ix.filled()),
            ('iy', iy.filled()),
            ('idx', idx.filled())])))
    else:
        print('ix:', ix)
        print('iy:', iy)
        print('idx:', idx)

    return


# # Case moving diagonally into the lowest point on grid
# test_functions(np.linspace(-180.4, -178.4, 21), np.linspace(-80.4, -78.4, 21))

# Case should be in on the lowest corner of grid, but inside
test_functions(-180, -80)

# Should be inside first grid
test_functions(-179.1, -79)

# Should be outside in both dimensions
test_functions(-180.1, -80.4)

# Should be outside in one dimension
test_functions(-180.1, -79.9)

# In the centre of the whole grid
test_functions(0.0, 0.0)

# Far right grid
test_functions(180.0, 0.0)
