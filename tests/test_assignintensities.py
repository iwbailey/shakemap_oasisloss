# Test we can assign intensities to intensity bins and get the intensity id

# Dependencies
import sys
import numpy as np
import pandas as pd

from shakemap_oasisloss import BinIntervals

# Parameters ------------------------------------------------------------------

np.random.seed(1234)

# Define the bin edges
binedges = np.linspace(5.45, 10.05, 47)
binedges[-1] = float("inf")  # open upper bin

# Random intensities
intensities = np.random.uniform(5.0, 12.0, size=20)

pd.options.display.max_rows = 10

# Script ----------------------------------------------------------------------

# Set up the intensity bins
intensbins = BinIntervals(binedges, closed='left')

# Create a dataframe containing the observed intensities
df = pd.DataFrame(intensities, columns=['obs'],
                  index=range(0, len(intensities)))
print("IN:")
print(df)

# Get rid of intensities below the cutoff
isin = np.vectorize(intensbins.bin_id.index.contains)
print("\nIgnoring %i intensities below %.2f..." %
      (df[~isin(df.obs)].count(), intensbins.min()))

print(df[~isin(df.obs)])
df = df[isin(df.obs)]

# Get the bin for each of the observations
df['bin_id'] = intensbins.bin_id[df.obs.values].values
df['bin_from'] = intensbins.bin_id[df.obs.values].index.left
df['bin_to'] = intensbins.bin_id[df.obs.values].index.right

print(df)

sys.exit()
