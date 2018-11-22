"""
 Damage function based on fragility curve
"""
# TODO: Description

import numpy as np
import pandas as pd
from scipy import interpolate
import pdb


class DamageFunction:
    """Class for an oasis style damage function """
    def __init__(self, vulnId, frag, damageStateDict, intensBins,
                 drBins):
        """ Constructor """

        # Assign the vuln id
        self.vulnId = vulnId

        # Interpolate the fragility curve of each damage state to get
        # exceedance probabilities at each intensity
        exprob_df = pd.DataFrame(columns=frag.damagestates(), index=intensBins)
        for c in frag.damagestates():
            exprob_df[c] = frag.interp_damagestate(intensBins.mid, c)

        # Save the dataframe as a property of the class
        self.exprobcurves = exprob_df

        # Assign the damage state names to  damage ratios
        drVals = [damageStateDict[x] for x in frag.damagestates()]

        # Interpolation function for current damage ratios to higher resolution
        def myinterp(x):
            return interpolate.pchip_interpolate(drVals, x, drBins.left.values)

        # Run the interpolation for each row, i.e. each intensity bin, output
        # the prob of exceeding the damage ratio
        probEx = np.apply_along_axis(myinterp, axis=1, arr=exprob_df.values)

        # Convert to probability of within this damage ratio. The final bin
        # remains the same.
        prob = probEx
        prob[:, :-1] = np.diff(-probEx, axis=1)

        # store as a data frame, with intensities as rows, damage as columns
        self.prob = pd.DataFrame(prob, index=intensBins, columns=drBins)

        # TODO deal with when the minimum

        return

    def vulnarr_to_oasis(self, intensbins, drbins, minProb=1e-6):
        """Convert from a vulnerability matrix with damage states as different rows,
        intensity bins as different columns, each column providing the discrete
        prob distribution

        """

        # Convert to damage function from 2-d array to  single column
        p = self.prob.stack().to_frame(name='prob')
        p.index.set_names(['intens_bin', 'dmg_bin'], inplace=True)

        # Drop the low probability ones
        p = p[p.prob >= minProb]

        # Join with the intensity bins
        intensbins = intensbins.bin_id.to_frame(name='intensity_bin_id')
        intensbins.index.name = 'intens_bin'
        p = p.join(intensbins, how='left')

        # Join with the damage bins
        drbins = drbins.bin_id.to_frame(name='damage_bin_id')
        drbins.index.name = 'dmg_bin'
        p = p.join(drbins, how='left')

        # Drop the multi-index
        p = p.reset_index(drop=True)

        # Assign the vulnerability id
        p = p.assign(vulnerability_id=self.vulnId)

        # Return the necessary columns in the right order
        # TODO: check order is correct
        return p.loc[:, ['vulnerability_id', 'intensity_bin_id',
                         'damage_bin_id', 'prob']]
