# Test we can create a set of damage bins for oasis

# Dependencies
import numpy as np
from shakemap_oasisloss import BinIntervals

# Define the bin edges
binedges = np.linspace(0.0, 1.0, 101)
binedges = np.insert(binedges, 0, 0.0)

# Set up the damage bins
damagebins = BinIntervals(binedges, 'right')

# Check ok
damagebins.check_damagebins()

# Display in oasis format
print(damagebins.to_oasisdf())
