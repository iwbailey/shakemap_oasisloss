#
# Test Creating a footprint that accounts for uncertainty
#

import numpy as np
import pandas as pd
from scipy.stats import norm

from shakemap_oasisloss import BinIntervals

# Initialize random seed
np.random.seed(12345)

# Number of locations with intensity
nLoc = 10

# Define bin edges
binEdges = np.linspace(5.0, 10.0, 6)
binEdges[-1] = np.Inf

# Create table of means and standard deviations
footprint0 = pd.DataFrame({
    'areaperil_id': 1 + np.arange(0, nLoc),
    'mean': 7.5 + 5.0 * np.random.random_sample(nLoc),
    'std': np.random.random_sample(nLoc)})


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
        try:
            # This only works if mean is within an interval. Use try/catch
            # so we can return prob=0.0 for all intervals in that case
            prob[intervals.get_loc(m0)] = 1.0
        except KeyError:
            if type(m0) is float:
                print("WARNING: mean %f out of range" % m0)
            else:
                raise
        except Exception:
            raise

    else:
        # CDF is Prob(X<=x)
        # ... so Prob(X<=x2) - Prob(X<=x1) gives Prob(x1 < X <= x2)
        # ? If we want Prob(x1 <= X < X2), it won't make a difference
        prob2 = norm.cdf(intervals.right, m0, s)
        prob1 = norm.cdf(intervals.left, m0, s)
        prob = prob2 - prob1

    return prob


def calc_probs_df(df, intervals):
    return calc_probs(intervals, df[0], df[1])


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

# Run for entire table simultaneously


# Reshape array
def my_add(df, x=1):
    return [df[0], df[1], x, df[0] + df[1], df[0]/df[1]]

print(footprint0.loc[:, ['mean', 'std']].apply(lambda x: my_add(x, 2), axis=1))

footprint0.loc[:, ['mean', 'std']].apply(lambda x: calc_probs_df(x, bins.df.index),
                                         axis=1)
