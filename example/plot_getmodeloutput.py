""" Plot the output """

import pandas as pd
from matplotlib import pyplot as plt
import seaborn as sns

from oasis_utils import read_csvtodf

# Parameters
ifile_getmodel = "./results/loccdf.csv"
pd.options.display.max_rows = 20
vulnId = 1
eventId = 1

# Read the output file
gm = read_csvtodf(ifile_getmodel)
gm = gm.loc[(gm.vulnerability_id == vulnId) & (gm.event_id == eventId)]
gm.drop(['vulnerability_id', 'event_id'], 1, inplace=True)

#gm3 = gm.groupby(["areaperil_id", "bin_mean"])['prob_to'].prod()
gm3 = gm.groupby(["areaperil_id", "bin_mean"])['prob_to'].max()

gm2 = gm3.to_frame().reset_index().pivot('areaperil_id', 'bin_mean', 'prob_to')

# Plot
f, ax2 = plt.subplots(figsize=(9, 6))
sns.heatmap(gm2, ax=ax2, cmap='Spectral')

plt.show()
