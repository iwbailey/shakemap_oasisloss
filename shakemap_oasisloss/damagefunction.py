"""
 Damage function based on fragility curve
"""
# TODO: Description

import numpy as np
import pandas as pd
from scipy import interpolate


class DamageFunction:
    """Class for an oasis style damage function """
    def __init__(self, vulnId, frag, damageStateDict, intensBinCentres,
                 drBinEdges):
        """ Constructor """

        # Assign the vuln id
        self.vulnId = vulnId

        # Interpolate the fragility curve exceedance probabilities to the
        # bottom of the bins
        df = pd.DataFrame(columns=frag.damagestates())
        for c in frag.damagestates():
            df[c] = frag.interp_damagestate(intensBinCentres, c)

        # Assign the intepolated results to the damage ratios
        drVals = [damageStateDict[x] for x in frag.damagestates()]

        # Interpolation function for current damage states to higher resolution
        def myinterp(x):
            return interpolate.pchip_interpolate(drVals, x, drBinEdges[:-1])

        # Run the interpolation for each row, i.e. each intensity bin, output
        # as array with intensity on rows, damage along columns
        probEx = (np.apply_along_axis(myinterp, axis=1, arr=df.values)).T

        # Store the discrete results
        self.prob = np.vstack((np.diff(-probEx, axis=0), probEx[-1, :]))

        # TODO deal with when the minimum

        return

    def vulnarr_to_oasis(self, minProb=1e-6):
        """Convert from a vulnerability matrix with damage states as different rows,
        intensity bins as different columns, each column providing the discrete
        prob distribution

        """

        nrow = self.prob.shape[0]
        ncol = self.prob.shape[1]

        damBinIdx = np.arange(1, nrow + 1)
        intensBinIdx = np.arange(1, ncol + 1)

        oasisVuln = pd.DataFrame.from_dict({'vulnerability_id':
                                            np.repeat(self.vulnId, nrow*ncol),
                                            'intensity_bin_index':
                                            np.tile(intensBinIdx, nrow),
                                            'damage_bin_index':
                                            np.repeat(damBinIdx, ncol),
                                            'prob':
                                            self.prob.flatten()})

        # Get rid of zeros

        return oasisVuln[oasisVuln.prob >= minProb]
