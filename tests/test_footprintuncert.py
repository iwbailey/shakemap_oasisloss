#
# Test Creating a footprint that accounts for uncertainty
#

import sys
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from scipy.stats import norm
import time

from shakemap_oasisloss import BinIntervals
from shakemap_oasisloss.footprint import calc_binprobs_norm
from shakemap_oasisloss.footprint import assign_probtobin

# Zero std deviation checks -------

# Test the impact of interval closed left vs right
print("\nCheck case where std dev == 0 and mean is on boundary...")
print("\tInterval is closed right, prob:")
p = calc_binprobs_norm(8.0, 0.0, np.array([7.0, 8.0, 9.0]), closed='right')

print(p)

print("\tInterval is closed left, prob:")
p = calc_binprobs_norm(8.0, 0.0, np.array([7.0, 8.0, 9.0]), closed='left')

print(p)

print("\tOut of range, prob:")
p = calc_binprobs_norm(6.0, 0.0, np.array([7.0, 8.0, 9.0]))
print(p)


# Case with standard deviation generated randomly  --------------

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

# Check the function works for a single row
m, s = footprint0.loc[3, :].values[[1, 2]]
print("\nTest case for m=%.3f; s=%.3f:" % (m, s))

p = calc_binprobs_norm(m, s, binEdges)
print(bins.df.assign(prob=p))

print("Sum Probs = %.3f" % sum(p))

# Calculate the probability for all mean/sd rows

# We have to repeat the existing data frame for each intensity bin.
outdf = footprint0
outdf = pd.concat([outdf]*len(bins.df), ignore_index=True)

# OPTION 1: Calculate a probability array
print('**1')
tic = time.time()


def myfun(x):
    """Need function to take a single argument"""
    return calc_binprobs_norm(x[0], x[1], binEdges)


probs = np.apply_along_axis(myfun, axis=1,
                            arr=footprint0.loc[:, ['m', 's']].values)

outdf = outdf.assign(bin_id=np.repeat(bins.df.bin_id.values, len(footprint0)))
outdf = outdf.assign(prob1=probs.flatten('F'))
toc = time.time()
print("%.1e s elapsed since **1" % (toc-tic))


# OPTION 1B
tic = time.time()

def myfun2(x):
    return(norm.cdf(x, footprint0.m, footprint0.s))


probs2 = np.apply_along_axis(myfun2, axis=1, arr=binEdges[:, None])

toc = time.time()
print("%.1e s elapsed since **1" % (toc-tic))

# OPTION 2: Calculate each row in the pandas array

tic = time.time()
outdf = outdf.assign(x1=np.repeat(bins.df.index.left.values, len(footprint0)))
outdf = outdf.assign(x2=np.repeat(bins.df.index.right.values, len(footprint0)))
outdf = outdf.assign(prob2=(norm.cdf(outdf.x2, outdf.m, outdf.s) -
                            norm.cdf(outdf.x1, outdf.m, outdf.s)))

toc = time.time()
print("%.1e s elapsed" % (toc-tic))

# OPTION 3: filter out intervals and then calculate each row
maxNsigma = 5

tic = time.time()
isKeep = ((outdf.x1 - outdf.m < maxNsigma*outdf.s) &
          (outdf.m - outdf.x2 < maxNsigma*outdf.s))
outdf2 = outdf[isKeep]
toc = time.time()
print("%.1e s elapsed" % (toc-tic))

sys.exit()
# outdf = pd.concat([outdf]*len(bins.df), ignore_index=True)

# # Convert to a data frame.
# outdf['intensity_bin_index'] = np.tile(intensbins.df.bin_id.values,
#                                                len(self.df))
# outdf['prob'] = probs.flatten()


# Convert the probability array into a dataframe
# outdf = pd.DataFrame({
#     'areaperil_id': np.repeat(footprint0.areaperil_id.values, len(bins.df)),
#     'bin_id':
#     'prob': probs.flatten()})

sys.exit()

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
