#
# Test Creating a footprint that accounts for uncertainty
#

import sys
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from scipy.stats import norm

from shakemap_oasisloss import BinIntervals

# Initialize random seed
np.random.seed(12345)

# Number of locations with intensity
nLoc = 10

# Define bin edges
binEdges = np.linspace(5.0, 10.0, 11)
binEdges[-1] = np.Inf

# Create table of means and standard deviations
footprint0 = pd.DataFrame({
    'areaperil_id': 1 + np.arange(0, nLoc),
    'm': 5.0 + 5.0 * np.random.random_sample(nLoc),
    's': 2*np.random.random_sample(nLoc)})


print("IN:")
print(footprint0)

# Define intensity bin intervals
bins = BinIntervals(binEdges)

print("\nIntervals:")
print(bins.df)

# Define function to calculate uncertainty


def calc_probs(intervals, m0, s):
    """Calculate the discrete probabilties for each interval

    """

    if s == 0:
        # Standard deviation = 0, just assign m0
        prob = np.zeros(np.shape(intervals))
        if intervals.contains(m0):
            prob[intervals.get_loc(m0)] = 1.0
        else:
            print("WARNING: mean %f out of range" % m0)

    else:
        # CDF is Prob(X<=x)
        # ... so Prob(X<=x2) - Prob(X<=x1) gives Prob(x1 < X <= x2)
        # ? If we want Prob(x1 <= X < X2), it won't make a difference
        prob2 = norm.cdf(intervals.right, m0, s)
        prob1 = norm.cdf(intervals.left, m0, s)
        prob = prob2 - prob1

    return prob




# Check the function works for a single bin
m, s = footprint0.loc[3, :].values[[1, 2]]
print("\nTest case for m=%.3f; s=%.3f:" % (m, s))

p = calc_probs(bins.df.index, m, s)
print(bins.df.assign(prob=p))

print("Sum Probs = %.3f" % sum(p))

# Test the impact of interval closed left vs right
print("\nCheck case where std dev == 0 and mean is on boundary...")
print("\tInterval is closed right, prob:")
p = calc_probs(pd.IntervalIndex.from_breaks([7.0, 8.0, 9.0], closed='right'),
               8.0, 0.0)
print(p)

print("\tInterval is closed left, prob:")
p = calc_probs(pd.IntervalIndex.from_breaks([7.0, 8.0, 9.0], closed='left'),
               8.0, 0.0)
print(p)

print("\tOut of range, prob:")
p = calc_probs(pd.IntervalIndex.from_breaks([7.0, 8.0, 9.0], closed='left'),
               6.0, 0.0)
print(p)

# Calculate the probability for all mean/sd combinations

# Create function to take a single row of mean/sd
def calc_probs_df(df):
    probs = calc_probs(bins.df.index, df[0], df[1])
    return probs

# Convert mean and std dev to an array, then calculate the probs on
# each row of that array. The result will have each bin in columns,
# each obs in the rows
probs = np.apply_along_axis(calc_probs_df,
                            axis=1,
                            arr=footprint0.loc[:, ['m', 's']].values)


# Convert the probability array into a dataframe
outdf = pd.DataFrame({
    'areaperil_id': np.repeat(footprint0.areaperil_id.values, len(bins.df)),
    'bin_id': np.tile(bins.df.bin_id.values, len(footprint0)),
    'prob': probs.flatten()})

# Get rid of zero probabilities
outdf = outdf[outdf.prob > 1e-15]
print(outdf)

# Check lot the array
plt.imshow(probs.transpose(), interpolation=None, origin='lower',
           extent=(0.5, nLoc+0.5, binEdges[0], 2*binEdges[-2] - binEdges[-3]))
plt.plot(np.arange(1, nLoc+1), footprint0.m.values, '+r')
plt.errorbar(np.arange(1, nLoc+1), footprint0.m.values,
             yerr=0.5*footprint0.s.values, fmt="none", ecolor='r')
plt.xticks(1 + np.arange(0, nLoc))
plt.xlabel('areaperil_id')
plt.ylabel('intensity')
plt.show()
