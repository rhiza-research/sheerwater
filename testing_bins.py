# determining truth and estimate thresholds

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import seaborn as sns


def goodbins(df, debug=False, **kwargs):
    """
    Determine the thresholds for the truth and estimate distributions.
    df - truth as columns, estimate as rows
    """
    # tune-able parameters
    defaults = {'minbinwidth': 2, 'mindist': 0.5, 'maxbinwidth': 10, 'mode': 'hellinger'}
    # merge defaults with kwargs - override defaults with kwargs
    kwargs = {**defaults, **kwargs}
    minbinwidth = kwargs['minbinwidth']
    mindist = kwargs['mindist']
    maxbinwidth = kwargs['maxbinwidth']
    mode = kwargs['mode']
    def get_distribution(df):
        df = df.sum(axis=1)
        return df / df.sum()

    def get_distance(P, Q, mode='hellinger'):
        if mode == 'hellinger':
            return np.sqrt(0.5 * np.sum((np.sqrt(P) - np.sqrt(Q)) ** 2))
        elif mode == 'kl':
            return np.sum(P * np.log(P / Q))
        elif 'overlap' in mode:
            pct = float(mode.split('_')[-1]) / 100
            idx = np.min(np.where(np.cumsum(P.values) >= pct))
            q_mass = np.cumsum(Q.values)[idx]
        return 1-q_mass

    tbinlo, tbinhi = [], []
    ebinlo, ebinhi = [], []

    prevlo, prevhi = 0, minbinwidth
    nxtlo, nxthi = minbinwidth, 2*minbinwidth
    gap = False

    while nxthi <= len(df.columns):
        Pprev = get_distribution(df.iloc[:, prevlo:prevhi])
        Pnxt = get_distribution(df.iloc[:, nxtlo:nxthi])
        dist = get_distance(Pprev, Pnxt, mode=mode)
        if debug:
            print(f"""=====
            in gap?: {gap},
            prev bin: {prevlo}-{prevhi},
            next bin: {nxtlo}-{nxthi},
            dist: {dist},
            """)

        if not gap:
            if dist > mindist: # we are far enough from previous bin to start a new one
                # close
                tbinlo.append(prevlo)
                tbinhi.append(prevhi)
                prevlo, prevhi = nxtlo, nxthi
                nxtlo, nxthi = nxthi, nxthi + minbinwidth
            elif (prevhi - prevlo) >= maxbinwidth: # bin is at width limit
                # close
                tbinlo.append(prevlo)
                tbinhi.append(prevhi)
                nxtlo, nxthi = nxtlo + 1, nxthi + 1
                gap = True
            else: # we are still within the same bin, expand it
                prevhi += 1
                nxtlo, nxthi = nxtlo + 1, nxthi + 1
        else: # we are in the gap mode
            if dist > mindist: # we are far enough from previous bin to start a new one
                prevlo, prevhi = nxtlo, nxthi
                nxtlo, nxthi = nxthi, nxthi + minbinwidth
                gap = False
            else: # keep widening the gap
                nxtlo, nxthi = nxtlo + 1, nxthi + 1
    # close the last bin
    if not gap:
        tbinlo.append(prevlo)
        tbinhi.append(prevhi)
    return tbinlo, tbinhi

if __name__ == "__main__":
    # load a joint distribution of station and satellite data
    df = pd.read_pickle('histograms/kenya_sample.pkl')
    # plot the joint distribution
    ax = sns.heatmap(np.log(df + 1), cmap='viridis')
    ax.invert_yaxis()

    tbinlo, tbinhi = goodbins(df, debug=True, mindist=0.8, maxbinwidth=30, mode='overlap_80')
    import pdb; pdb.set_trace() 