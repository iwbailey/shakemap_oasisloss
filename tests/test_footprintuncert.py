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

# Minimum probabilty to keep
minProb = 1e-6

# Define bin edges
binEdges = np.linspace(5.0, 10.0, 11)
binEdges[-1] = np.Inf

# Create table of means and standard deviations
footprint0 = pd.DataFrame({
    'areaperil_id': 1 + np.arange(0, nLoc),
    'm': 5.0 + 5.0 * np.random.random_sample(nLoc),
    's': 1*np.random.random_sample(nLoc)})


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
print("Calculating all probabilities for all observations...\n")


def get_probs_v1(footprint0, bins, minProb):
    """ Calculate a probability array, then flatten it """
    # We have to repeat the existing data frame for each intensity bin.
    outdf = footprint0
    outdf = pd.concat([outdf]*len(bins.df), ignore_index=True)

    # Calculate bin edges
    breaks = np.append(bins.df.index.left.values,
                       bins.df.index.max().right)

    def myfun(x):
        """Need function to take a single argument"""
        return calc_binprobs_norm(x[0], x[1], breaks)

    # Calculate an array of probabilities
    probs = np.apply_along_axis(myfun, axis=1,
                                arr=footprint0.loc[:, ['m', 's']].values)

    outdf = outdf.assign(bin_id=np.repeat(bins.df.bin_id.values,
                                          len(footprint0)))
    outdf = outdf.assign(prob=probs.flatten('F'))

    # Get rid of values that are too low
    return outdf[outdf.prob > minProb], probs


# Time it
print("\n**")
tic = time.time()
outdf, probs = get_probs_v1(footprint0, bins, minProb)
print("%.1e s elapsed since **" % (time.time()-tic))


def print_fp(outdf):
    """ Display the result """
    print(outdf.sort_values(by=['areaperil_id', 'bin_id']).head(25))

    # Check the probabiltiies sum to 1
    print("\nCheck sum(prob):")
    print(outdf.groupby(['areaperil_id', 'm', 's']).agg({'prob': sum}))


# Display the result
print_fp(outdf)

# Check plot of the array
plt.imshow(probs.transpose(), interpolation=None, origin='lower',
           extent=(0.5, nLoc+0.5, binEdges[0], 2*binEdges[-2] - binEdges[-3]))
plt.plot(np.arange(1, nLoc+1), footprint0.m.values, '+r')
plt.errorbar(np.arange(1, nLoc+1), footprint0.m.values,
             yerr=0.5*footprint0.s.values, fmt="none", ecolor='r')
plt.xticks(1 + np.arange(0, nLoc))
plt.xlabel('areaperil_id')
plt.ylabel('intensity')
plt.show()


# Test alternative approach to calculating probabilties
def get_probs_v2(footprint0, bins, minProb):

    # Merge all combinations of the footprint and bin intervals using a common
    # key, then drop the key
    outdf = pd.merge(footprint0.assign(key=0),
                     bins.to_leftright().assign(key=0),
                     on='key', how='outer').drop('key', 1)

    # Remove bins we know will be zero prob
    maxNsigma = norm.ppf(1-minProb, 0, 1)
    isKeep = ((outdf.left - outdf.m < maxNsigma*outdf.s) &
              (outdf.m - outdf.right < maxNsigma*outdf.s))
    outdf = outdf[isKeep]

    # Calculate the probabilties
    outdf = outdf.assign(prob=(norm.cdf(outdf.right, outdf.m, outdf.s) -
                               norm.cdf(outdf.left, outdf.m, outdf.s)))

    return outdf


print("\nAlternative approach 1 **")
tic = time.time()
outdf2 = get_probs_v2(footprint0, bins, minProb)
print("%.1e s elapsed since **" % (time.time()-tic))

print_fp(outdf2)
sys.exit()

outdf = outdf.assign(prob2=(norm.cdf(outdf.x2, outdf.m, outdf.s) -
                            norm.cdf(outdf.x1, outdf.m, outdf.s)))

toc = time.time()
print("%.1e s elapsed" % (toc-tic))

sys.exit()
